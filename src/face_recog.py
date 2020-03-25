import cv2
import numpy as np
import onnx
import onnxruntime as ort
from onnx_tf.backend import prepare
import argparse

class UltraLightFaceRecog:
    def area_of(self, left_top, right_bottom):
        """
        Compute the areas of rectangles given two corners.
        Args:
            left_top (N, 2): left top corner.
            right_bottom (N, 2): right bottom corner.
        Returns:
            area (N): return the area.
        """
        hw = np.clip(right_bottom - left_top, 0.0, None)
        return hw[..., 0] * hw[..., 1]

    def iou_of(self, boxes0, boxes1, eps=1e-5):
        """
        Return intersection-over-union (Jaccard index) of boxes.
        Args:
            boxes0 (N, 4): ground truth boxes.
            boxes1 (N or 1, 4): predicted boxes.
            eps: a small number to avoid 0 as denominator.
        Returns:
            iou (N): IoU values.
        """
        overlap_left_top = np.maximum(boxes0[..., :2], boxes1[..., :2])
        overlap_right_bottom = np.minimum(boxes0[..., 2:], boxes1[..., 2:])

        overlap_area = self.area_of(overlap_left_top, overlap_right_bottom)
        area0 = self.area_of(boxes0[..., :2], boxes0[..., 2:])
        area1 = self.area_of(boxes1[..., :2], boxes1[..., 2:])
        return overlap_area / (area0 + area1 - overlap_area + eps)

    def hard_nms(self, box_scores, iou_threshold, top_k=-1, candidate_size=200):
        """
        Perform hard non-maximum-supression to filter out boxes with iou greater
        than threshold
        Args:
            box_scores (N, 5): boxes in corner-form and probabilities.
            iou_threshold: intersection over union threshold.
            top_k: keep top_k results. If k <= 0, keep all the results.
            candidate_size: only consider the candidates with the highest scores.
        Returns:
            picked: a list of indexes of the kept boxes
        """
        scores = box_scores[:, -1]
        boxes = box_scores[:, :-1]
        picked = []
        indexes = np.argsort(scores)
        indexes = indexes[-candidate_size:]
        while len(indexes) > 0:
            current = indexes[-1]
            picked.append(current)
            if 0 < top_k == len(picked) or len(indexes) == 1:
                break
            current_box = boxes[current, :]
            indexes = indexes[:-1]
            rest_boxes = boxes[indexes, :]
            iou = self.iou_of(
                rest_boxes,
                np.expand_dims(current_box, axis=0),
            )
            indexes = indexes[iou <= iou_threshold]

        return box_scores[picked, :]

    def predict(self, width, height, confidences, boxes, prob_threshold, iou_threshold=0.5, top_k=-1):
        """
        Select boxes that contain human faces
        Args:
            width: original image width
            height: original image height
            confidences (N, 2): confidence array
            boxes (N, 4): boxes array in corner-form
            iou_threshold: intersection over union threshold.
            top_k: keep top_k results. If k <= 0, keep all the results.
        Returns:
            boxes (k, 4): an array of boxes kept
            labels (k): an array of labels for each boxes kept
            probs (k): an array of probabilities for each boxes being in corresponding labels
        """
        boxes = boxes[0]
        confidences = confidences[0]
        picked_box_probs = []
        picked_labels = []
        for class_index in range(1, confidences.shape[1]):
            probs = confidences[:, class_index]
            mask = probs > prob_threshold
            probs = probs[mask]
            if probs.shape[0] == 0:
                continue
            subset_boxes = boxes[mask, :]
            box_probs = np.concatenate([subset_boxes, probs.reshape(-1, 1)], axis=1)
            box_probs = self.hard_nms(box_probs,
            iou_threshold=iou_threshold,
            top_k=top_k,
            )
            picked_box_probs.append(box_probs)
            picked_labels.extend([class_index] * box_probs.shape[0])
        if not picked_box_probs:
            return np.array([]), np.array([]), np.array([])
        picked_box_probs = np.concatenate(picked_box_probs)
        picked_box_probs[:, 0] *= width
        picked_box_probs[:, 1] *= height
        picked_box_probs[:, 2] *= width
        picked_box_probs[:, 3] *= height
        return picked_box_probs[:, :4].astype(np.int32), np.array(picked_labels), picked_box_probs[:, 4]

    def load_model(self, model_path):
        onnx_model = onnx.load(model_path)
        predictor = prepare(onnx_model)
        self.ort_session = ort.InferenceSession(model_path)
        self.input_name = self.ort_session.get_inputs()[0].name

    def blur_faces(self, model_path, video_input, video_output):
        
        self.load_model(model_path)
        
        # Video properties 
        video = cv2.VideoCapture(video_input)
        ret, frame = video.read()
        height , width , layers =  frame.shape
        new_h = height//2
        new_w = width//2
        size = (new_w, new_h)
        all_frames = []

        while True:
            ret, frame = video.read()
            
            if frame is not None:
                frame = cv2.resize(frame, (new_w, new_h)) 
                h, w, _ = frame.shape

                # preprocess img acquired
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # convert bgr to rgb
                img = cv2.resize(img, (640, 480)) # resize
                img_mean = np.array([127, 127, 127])
                img = (img - img_mean) / 128
                img = np.transpose(img, [2, 0, 1])
                img = np.expand_dims(img, axis=0)
                img = img.astype(np.float32)

                confidences, boxes = self.ort_session.run(None, {self.input_name: img})
                boxes, labels, probs = self.predict(w, h, confidences, boxes, 0.7)

                for i in range(boxes.shape[0]):
                    box = boxes[i, :]
                    x1, y1, x2, y2 = box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0,0,0), -1)
                    cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (80,18,236), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    text = f"face"
                    cv2.putText(frame, text, (x1 + 6, y2 - 6), font, 0.5, (255, 255, 255), 1)
                all_frames.append(frame)
            else:
                break
        self.save_local_video(all_frames, video_output, 30, size)



    def save_local_video(self, frames_array, filepath, speed, size):
        out = cv2.VideoWriter(filepath,cv2.VideoWriter_fourcc(*'DIVX'), round(speed), size)
        print("Frames array size: ", len(frames_array))
        for i in range(len(frames_array)):
            #cv2.imwrite('../tests/data/output/frames/frame_' + str(i) + '.png', frames_array[i])
            out.write(frames_array[i])

        out.release()
        print("> Video saved at ", filepath)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('-i', '--video_input', help='Input video path',
            default= '', dest='video_input')
    parser.add_argument('-o', '--video_output', help='Output video path',
            default= '', dest='video_output')
    parser.add_argument('-m', '--model_path', help='Model path',
            default= './models/ultra_light_640.onnx', dest='model_path')
    args = parser.parse_args()

    face_recog = UltraLightFaceRecog()
    face_recog.blur_faces(args.model_path, args.video_input, args.video_output)
