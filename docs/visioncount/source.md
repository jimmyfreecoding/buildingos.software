# 源代码提交页（智能楼宇AI感知物联系统 buildingos.visionCount）

## 提交要求
- 提供源程序的连续前30页与连续后30页；不足60页需提供全部源代码
- 每页不少于50行
- 源代码中不得包含公司名称、个人名称、文件名称
- 源代码总数量需与申请表保持一致

## 前30页
以下为前30页的连续源代码片段（AI推理引擎核心逻辑）。

```
import cv2
import numpy as np
import tensorrt as trt
import pycuda.driver as cuda
import pycuda.autoinit
import threading
import json
import os

# 全局推理锁，防止多线程同时调用 TensorRT 引擎导致 double free
trt_infer_lock = threading.Lock()

class YoloTensorRTEngine:
    """
    纯 TensorRT 实现，彻底脱离 Torch/Ultralytics 依赖。
    支持 YOLOv8/v11 的检测 (Detect) 和姿态 (Pose) 任务。
    """
    def __init__(self, engine_path, imgsz=640, conf_thres=0.25, iou_thres=0.45):
        self.engine_path = engine_path
        self.imgsz = (imgsz, imgsz) if isinstance(imgsz, int) else imgsz
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        
        # 1. 加载引擎并处理 Ultralytics Metadata
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.runtime = trt.Runtime(self.logger)
        
        engine_data = self._load_engine_data(engine_path)
        self.engine = self.runtime.deserialize_cuda_engine(engine_data)
        self.context = self.engine.create_execution_context()
        
        # 2. 分配显存/内存缓冲区
        self.inputs = []
        self.outputs = []
        self.bindings = []
        self.stream = cuda.Stream()
        
        for binding in self.engine:
            size = trt.volume(self.engine.get_tensor_shape(binding))
            dtype = trt.nptype(self.engine.get_tensor_dtype(binding))
            # 分配页锁定内存 (Host)
            host_mem = cuda.pagelocked_empty(size, dtype)
            # 分配显存 (Device)
            device_mem = cuda.mem_alloc(host_mem.nbytes)
            
            self.bindings.append(int(device_mem))
            if self.engine.get_tensor_mode(binding) == trt.TensorIOMode.INPUT:
                self.inputs.append({'host': host_mem, 'device': device_mem, 'name': binding})
            else:
                self.outputs.append({'host': host_mem, 'device': device_mem, 'name': binding, 'shape': self.engine.get_tensor_shape(binding)})

        # 自动推断任务类型
        self.is_pose = 'pose' in engine_path.lower()
        task_str = "POSE" if self.is_pose else "DETECT"
        print(f"✅ 纯 TensorRT 引擎加载成功: {os.path.basename(engine_path)} (Task: {task_str})")

    def _load_engine_data(self, path):
        """读取引擎文件并自动跳过 Ultralytics 的 JSON Metadata 头部"""
        with open(path, 'rb') as f:
            data = f.read()
            
        # 检查是否包含 Ultralytics 的 JSON 头部 (通常以 { 开头)
        if data.startswith(b'{'):
            try:
                # 寻找 JSON 结束标记后的第一个非空字符
                # Ultralytics 的格式通常是: {JSON}\0\0\0...TRT_MAGIC...
                # 寻找 '7b' ({) 到 第一个 'ptr' (TensorRT 的 magic tag)
                # 实际上最简单的方法是寻找 "ms" (magic string)
                # 或者寻找第一个 0x00 后的非 0 区域
                # 这里使用更稳健的方法：定位 TensorRT 的序列化特征
                idx = data.find(b'ptr', 0, 1024) # TensorRT 10.x 之前的特征
                if idx == -1:
                    idx = data.find(b'pt7', 0, 1024) # TensorRT 10.x 之后的特征
                
                if idx != -1:
                    # 向上寻找第一个 0x00 (JSON 后的填充)
                    # 实际上直接从 idx 开始就是正确的 TRT 序列化数据
                    return data[idx:]
            except:
                pass
        return data

    def predict(self, img, conf_thres=None):
        if img is None:
            return []
            
        actual_conf = conf_thres if conf_thres is not None else self.conf_thres
        
        # 1. 预处理
        blob, ratio, (pad_w, pad_h) = self.preprocess(img)
        
        # 2. 推理 (加锁防止 double free)
        with trt_infer_lock:
            np.copyto(self.inputs[0]['host'], blob.ravel())
            cuda.memcpy_htod_async(self.inputs[0]['device'], self.inputs[0]['host'], self.stream)
            
            # 执行异步推理 (适配不同版本的 TensorRT API)
            try:
                self.context.execute_async_v3(stream_handle=self.stream.handle)
            except:
                self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)
            
            for out in self.outputs:
                cuda.memcpy_dtoh_async(out['host'], out['device'], self.stream)
            self.stream.synchronize()
        
        # 3. 后处理 (NMS)
        output = self.outputs[0]['host'].reshape(self.outputs[0]['shape'])
        return self.postprocess(output, img.shape[:2], ratio, (pad_w, pad_h), actual_conf)

    def preprocess(self, img):
        """保持比例的缩放 (Letterbox)"""
        shape = img.shape[:2]  # current shape [height, width]
        new_shape = self.imgsz
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
        
        new_unpad = (int(round(shape[1] * r)), int(round(shape[0] * r)))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
        dw /= 2
        dh /= 2
        
        if shape[::-1] != new_unpad:
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
            
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=(114, 114, 114))
        
        # HWC -> CHW, BGR -> RGB, /255.0
        img = img.transpose((2, 0, 1))[::-1]
        img = np.ascontiguousarray(img).astype(np.float32) / 255.0
        return img, r, (dw, dh)

    def postprocess(self, output, orig_shape, ratio, pad, conf_thres):
        """解析 YOLOv8/v11 的输出张量"""
        # output shape: (1, 4 + num_classes [+ 51 if pose], 8400)
        output = output[0] # remove batch dim -> (C, 8400)
        output = output.transpose() # -> (8400, C)
        
        # YOLOv8-Pose: [x, y, w, h, score, kpt1_x, kpt1_y, kpt1_conf, ...]
        # YOLOv8-Detect: [x, y, w, h, cls1_score, cls2_score, ...]
        
        boxes_for_nms = []
        scores = []
        class_ids = []
        keypoints = []
        final_boxes = []
        
        if self.is_pose:
            # Pose 任务通常只有一个类别 (Person)
            mask = output[:, 4] > conf_thres
            valid_output = output[mask]
            
            if len(valid_output) == 0: return []
            
            curr_boxes = valid_output[:, :4]
            curr_scores = valid_output[:, 4]
            curr_kpts = valid_output[:, 5:]
            
            for i in range(len(valid_output)):
                x, y, w, h = curr_boxes[i]
                x1 = (x - w/2 - pad[0]) / ratio
                y1 = (y - h/2 - pad[1]) / ratio
                x2 = (x + w/2 - pad[0]) / ratio
                y2 = (y + h/2 - pad[1]) / ratio
                
                # NMSBoxes 需要 [x, y, w, h]
                boxes_for_nms.append([int(x1), int(y1), int(x2-x1), int(y2-y1)])
                final_boxes.append([int(x1), int(y1), int(x2), int(y2)])
                scores.append(float(curr_scores[i]))
                class_ids.append(0) 
                
                kpts = curr_kpts[i].reshape(-1, 3)
                kpts[:, 0] = (kpts[:, 0] - pad[0]) / ratio
                kpts[:, 1] = (kpts[:, 1] - pad[1]) / ratio
                keypoints.append(kpts.flatten().tolist())
        else:
            # 检测任务
            num_classes = output.shape[1] - 4
            all_scores = output[:, 4:]
            max_scores = np.max(all_scores, axis=1)
            mask = max_scores > conf_thres
            valid_output = output[mask]
            
            if len(valid_output) == 0: return []
            
            curr_boxes = valid_output[:, :4]
            curr_scores = np.max(valid_output[:, 4:], axis=1)
            curr_cls = np.argmax(valid_output[:, 4:], axis=1)
            
            for i in range(len(valid_output)):
                x, y, w, h = curr_boxes[i]
                x1 = (x - w/2 - pad[0]) / ratio
                y1 = (y - h/2 - pad[1]) / ratio
                x2 = (x + w/2 - pad[0]) / ratio
                y2 = (y + h/2 - pad[1]) / ratio
                
                boxes_for_nms.append([int(x1), int(y1), int(x2-x1), int(y2-y1)])
                final_boxes.append([int(x1), int(y1), int(x2), int(y2)])
                scores.append(float(curr_scores[i]))
                class_ids.append(int(curr_cls[i]))
        
        # NMS
        indices = cv2.dnn.NMSBoxes(boxes_for_nms, scores, conf_thres, self.iou_thres)
        
        final_results = []
        if len(indices) > 0:
            for i in indices.flatten():
                res = {
                    "bbox": final_boxes[i],
                    "conf": scores[i],
                    "class_id": class_ids[i]
                }
                if self.is_pose:
                    res["keypoints_raw"] = keypoints[i]
                final_results.append(res)
                
        return final_results

import cv2
import numpy as np
import threading

trt_infer_lock = threading.Lock()

# 标准 COCO 80 类别列表
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]

# COCO 91 类别到 80 类别的映射 (用于解决 91 类模型的索引偏移)
# 注意：91 类中索引 1 是人，但在 80 类中索引 0 是人。
COCO_91_TO_80 = {
    1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 13: 11, 14: 12, 15: 13, 16: 14, 17: 15,
    18: 16, 19: 17, 20: 18, 21: 19, 22: 20, 23: 21, 24: 22, 25: 23, 27: 24, 28: 25, 31: 26, 32: 27, 33: 28, 34: 29,
    35: 30, 36: 31, 37: 32, 38: 33, 39: 34, 40: 35, 41: 36, 42: 37, 43: 38, 44: 39, 46: 40, 47: 41, 48: 42, 49: 43,
    50: 44, 51: 45, 52: 46, 53: 47, 54: 48, 55: 49, 56: 50, 57: 51, 58: 52, 59: 53, 60: 54, 61: 55, 62: 56, 63: 57,
    64: 58, 65: 59, 67: 60, 70: 61, 72: 62, 73: 63, 74: 64, 75: 65, 76: 66, 77: 67, 78: 68, 79: 69, 80: 70, 81: 71,
    82: 72, 84: 73, 85: 74, 86: 75, 87: 76, 88: 77, 89: 78, 90: 79
}

class RFDETRTensorRTEngine:
    def __init__(self, engine_path, conf_thres=0.25, person_class_id=0, max_det=100):
        self.engine_path = engine_path
        self.conf_thres = float(conf_thres)
        self.person_class_id = int(person_class_id)
        self.max_det = int(max_det)
        self.source_name = "rf-detr-trt"
        self.classes = COCO_CLASSES

        try:
            import tensorrt as trt
            import pycuda.driver as cuda
            import pycuda.autoinit  # noqa: F401
        except Exception as e:
            raise RuntimeError(f"RF-DETR TensorRT runtime dependencies missing: {e}")

        self.trt = trt
        self.cuda = cuda
        self.logger = trt.Logger(trt.Logger.WARNING)
        
        # 使用 autoinit 创建的全局上下文
        self.cuda_context = cuda.Context.get_current()
        
        with open(engine_path, "rb") as f, trt.Runtime(self.logger) as runtime:
            self.engine = runtime.deserialize_cuda_engine(f.read())
        if self.engine is None:
            raise RuntimeError(f"Failed to deserialize engine: {engine_path}")

        self.context = self.engine.create_execution_context()
        if self.context is None:
            raise RuntimeError("Failed to create TensorRT execution context")

        self.stream = cuda.Stream()
        self.input_name = None
        self.output_names = []
        self.tensor_meta = {}
        self.bindings = []

        self._init_io()
        print(f"✅ RF-DETR Engine Loaded: {engine_path}")

    def _init_io(self):
        trt = self.trt
        cuda = self.cuda

        num_tensors = self.engine.num_io_tensors
        self.bindings = [0] * num_tensors

        for i in range(num_tensors):
            name = self.engine.get_tensor_name(i)
            mode = self.engine.get_tensor_mode(name)
            if mode == trt.TensorIOMode.INPUT:
                self.input_name = name
                shape = list(self.engine.get_tensor_shape(name))
                if -1 in shape:
                    profile_shape = self.engine.get_tensor_profile_shape(name, 0)[1]
                    shape = list(profile_shape)
                    self.context.set_input_shape(name, tuple(shape))
            else:
                self.output_names.append(name)
                shape = list(self.context.get_tensor_shape(name))
                if -1 in shape:
                    profile_shape = self.engine.get_tensor_profile_shape(name, 0)[1]
                    shape = list(profile_shape)
            dtype = trt.nptype(self.engine.get_tensor_dtype(name))
            size = int(trt.volume(tuple(shape)))
            host = cuda.pagelocked_empty(size, dtype)
            device = cuda.mem_alloc(host.nbytes)
            self.tensor_meta[name] = {
                "shape": tuple(shape),
                "dtype": dtype,
                "host": host,
                "device": device,
                "index": i
            }
            self.bindings[i] = int(device)
            try:
                self.context.set_tensor_address(name, int(device))
            except Exception:
                pass

        if not self.input_name:
            raise RuntimeError("No input tensor found in engine")

        in_shape = self.tensor_meta[self.input_name]["shape"]
        if len(in_shape) != 4:
            raise RuntimeError(f"Unexpected input shape: {in_shape}")
        self.batch, self.channels, self.input_h, self.input_w = in_shape

    def _preprocess(self, img):
        """
        根据截图表现优化的预处理：
        1. 许多 TensorRT 模型内部已集成归一化，外部只需 0-1 缩放
        2. 保持 Squash 缩放以匹配 app.py
        """
        orig_h, orig_w = img.shape[:2]
        resized = cv2.resize(img, (self.input_w, self.input_h), interpolation=cv2.INTER_LINEAR)
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # 【核心测试项】
        # 很多 TensorRT Engine 导出时自带了 Mean/Std，Python 层再做会导致“双重归一化”。
        # 目前暂时注释掉减均值操作，仅保留 0-1 缩放，排除模型“致盲”可能。
        x = rgb.astype(np.float32) / 255.0
        
        # mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        # std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        # x = (x - mean) / std
        
        x = np.transpose(x, (2, 0, 1))[None, ...]
        
        scale_x = self.input_w / orig_w
        scale_y = self.input_h / orig_h
        return x, scale_x, scale_y, orig_w, orig_h

    def _infer(self, input_tensor):
        cuda = self.cuda
        np.copyto(self.tensor_meta[self.input_name]["host"], input_tensor.ravel())
        cuda.memcpy_htod_async(self.tensor_meta[self.input_name]["device"], self.tensor_meta[self.input_name]["host"], self.stream)

        try:
            self.context.execute_async_v3(stream_handle=self.stream.handle)
        except Exception:
            self.context.execute_async_v2(bindings=self.bindings, stream_handle=self.stream.handle)

        outputs = {}
        for name in self.output_names:
            meta = self.tensor_meta[name]
            cuda.memcpy_dtoh_async(meta["host"], meta["device"], self.stream)
        self.stream.synchronize()

        for name in self.output_names:
            meta = self.tensor_meta[name]
            outputs[name] = np.array(meta["host"]).reshape(meta["shape"])
        return outputs

    def _parse_outputs(self, outputs, scale_x, scale_y, orig_w, orig_h, conf_thres=None):
        """
        针对 (1, 300, 4) dets 和 (1, 300, 91) labels 的专用解析逻辑：
        1. 分离张量：dets 为坐标，labels 为分类分数 (Logits)
        2. 坐标格式：dets 已经是 0-1 范围，不再做 Sigmoid
        3. 类别偏移：91 类通常包含背景，person 的索引为 1
        4. NMS 抑制：消除重叠冗余框
        """
        # --- 1. 深度诊断日志 ---
        print("\n" + "="*50)
        print("RF-DETR 91-CLASS ENGINE DETECTED")
        for k, v in outputs.items():
            print(f"Tensor: {k:15} | Shape: {str(v.shape):15} | Range: [{np.min(v):.2f}, {np.max(v):.2f}]")
        
        # 2. 锁定张量
        boxes_raw = outputs.get('dets')[0] if 'dets' in outputs else None
        logits_raw = outputs.get('labels')[0] if 'labels' in outputs else None

        if boxes_raw is None or logits_raw is None:
            for v in outputs.values():
                if v.ndim == 3 and v.shape[-1] == 4: boxes_raw = v[0]
                elif v.ndim == 3 and v.shape[-1] == 91: logits_raw = v[0]
        
        if boxes_raw is None or logits_raw is None:
            print("ERROR: Missing 'dets' or 'labels' tensors!")
            return []

        # 3. 执行分类分数计算
        scores_91 = 1 / (1 + np.exp(-np.clip(logits_raw, -15, 15)))
        
        max_scores_91 = np.max(scores_91, axis=1)
        max_indices_91 = np.argmax(scores_91, axis=1)
        
        actual_conf_thres = float(conf_thres) if conf_thres is not None else self.conf_thres
        
        # 4. 初步收集候选框用于 NMS
        candidates = []
        for i in range(len(max_scores_91)):
            if max_scores_91[i] >= actual_conf_thres:
                cx, cy, bw, bh = boxes_raw[i]
                
                # 解码为像素坐标
                x1 = (cx - bw / 2.0) * orig_w
                y1 = (cy - bh / 2.0) * orig_h
                x2 = (cx + bw / 2.0) * orig_w
                y2 = (cy + bh / 2.0) * orig_h
                
                # 边界剪裁
                x1, y1 = max(0, int(x1)), max(0, int(y1))
                x2, y2 = min(orig_w, int(x2)), min(orig_h, int(y2))
                
                if x1 < x2 and y1 < y2:
                    cls_id_91 = int(max_indices_91[i])
                    cls_id_80 = COCO_91_TO_80.get(cls_id_91, -1)
                    if cls_id_80 != -1:
                        candidates.append({
                            "bbox": [x1, y1, x2, y2],
                            "conf": float(max_scores_91[i]),
                            "class_id": cls_id_80,
                            "class_name": self.classes[cls_id_80]
                        })

        # 5. 执行 NMS (非极大值抑制)
        # 解决图中出现的“2个人被识别成5个候选人”的重叠框问题
        if not candidates: return []
        
        # 按分数降序排序
        candidates.sort(key=lambda x: x['conf'], reverse=True)
        results = []
        
        def calculate_iou(boxA, boxB):
            xA = max(boxA[0], boxB[0])
            yA = max(boxA[1], boxB[1])
            xB = min(boxA[2], boxB[2])
            yB = min(boxA[3], boxB[3])
            interArea = max(0, xB - xA) * max(0, yB - yA)
            boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
            boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
            iou = interArea / float(boxAArea + boxBArea - interArea + 1e-6)
            return iou

        while len(candidates) > 0:
            best = candidates.pop(0)
            results.append(best)
            
            # 过滤掉与当前最强框重叠度过高的同类框
            # 按照建议将阈值调低到 0.45 以更激进地消除重叠框
            remaining = []
            for item in candidates:
                if item['class_id'] == best['class_id'] and calculate_iou(best['bbox'], item['bbox']) > 0.45:
                    continue
                remaining.append(item)
            candidates = remaining
        
        if results:
            best_det = max(results, key=lambda x: x['conf'])
            print(f"✅ SUCCESS: Detected {best_det['class_name']} ({best_det['conf']:.3f}) after NMS")
            
        return results

    def predict(self, img, conf_thres=None):
        if img is None:
            return []
        
        # 关键：确保在推理线程中使用正确的 CUDA Context
        self.cuda_context.push()
        try:
            with trt_infer_lock:
                x, scale_x, scale_y, w, h = self._preprocess(img)
                outputs = self._infer(x)
                return self._parse_outputs(outputs, scale_x, scale_y, w, h, conf_thres=conf_thres)
        finally:
            self.cuda_context.pop()

import time
from datetime import datetime
import threading
import collections

class TimePeriod:
    WORKTIME = "worktime"
    OVERTIME = "overtime"
    NIGHT = "night"

class PresenceStateMachine:
    """
    文档 4. Presence（人员存在）判定逻辑
    实现分时段窗口策略，防误关灯。
    """
    def __init__(self, camera_id, config):
        self.camera_id = camera_id
        
        # 加载配置 (强制默认值)
        self.window_worktime = config.get("presence_window_default_minutes", 10) * 60
        self.window_overtime = config.get("presence_window_overtime_minutes", 15) * 60
        self.window_night = config.get("presence_window_night_minutes", 5) * 60
        
        # 状态机状态: IDLE, WINDOW_TRACKING, CONFIRM_OCCUPIED, CONFIRM_EMPTY
        self.state = "IDLE"
        
        # 当前窗口信息
        self.window_start_time = 0
        self.window_period_type = None
        self.window_duration = 0
        self.has_person_in_window = False
        
        self.lock = threading.Lock()

    def _get_current_period(self):
        """根据当前系统时间判断所属时段 (简化实现，实际可解析 HH:MM)"""
        hour = datetime.now().hour
        if 9 <= hour < 19:
            return TimePeriod.WORKTIME, self.window_worktime
        elif 19 <= hour < 23:
            return TimePeriod.OVERTIME, self.window_overtime
        else:
            return TimePeriod.NIGHT, self.window_night

    def update(self, has_person_this_frame):
        """
        每次采样 (默认60s) 后调用此方法更新状态机。
        返回 (事件是否触发, 最终状态, 窗口时长分钟数, 所属时段)
        """
        with self.lock:
            now = time.time()
            event_triggered = False
            final_status = None

            # 1. 状态迁移: IDLE -> WINDOW_TRACKING
            if self.state == "IDLE":
                self.state = "WINDOW_TRACKING"
                self.window_start_time = now
                self.has_person_in_window = False
                # 时段边界规则 (强制): 窗口策略按启动时刻固定
                self.window_period_type, self.window_duration = self._get_current_period()
                print(f"[{self.camera_id}] Presence: 开启新窗口 ({self.window_period_type}, {self.window_duration//60}分钟)")

            # 2. 记录当前帧结果
            if has_person_this_frame:
                self.has_person_in_window = True
                
                # 状态迁移: WINDOW_TRACKING -> CONFIRM_OCCUPIED
                # 只要窗口内任一次有人，状态就是 CONFIRM_OCCUPIED
                if self.state == "WINDOW_TRACKING":
                    self.state = "CONFIRM_OCCUPIED"

            # 3. 检查窗口是否结束
            elapsed = now - self.window_start_time
            if elapsed >= self.window_duration:
                # 窗口收敛规则
                if self.has_person_in_window:
                    final_status = "occupied"
                else:
                    final_status = "empty"
                
                event_triggered = True
                
                print(f"[{self.camera_id}] Presence: 窗口结束. 结果={final_status}")
                
                # 重置状态并立即开启下一个窗口，确保连续性
                self.state = "WINDOW_TRACKING"
                self.window_start_time = now
                self.has_person_in_window = False
                self.window_period_type, self.window_duration = self._get_current_period()
                
            return event_triggered, final_status, self.window_duration // 60, self.window_period_type

class SmokingStateMachine:
    """
    Smoking（吸烟）判定逻辑 - 简化版
    不再管理时间窗口，仅负责记录告警状态。
    """
    def __init__(self, camera_id, config):
        self.camera_id = camera_id
        # 状态: IDLE, ALERT
        self.state = "IDLE"
        self.lock = threading.Lock()

    def confirm_smoke(self):
        """当检测到吸烟后调用"""
        with self.lock:
            self.state = "ALERT"
            print(f"[{self.camera_id}] Smoking: 发现吸烟动作，更新状态。")
            return True

    def reset(self):
        """重置状态"""
        with self.lock:
            self.state = "IDLE"

# 测试代码
if __name__ == "__main__":
    config = {}
    sm = PresenceStateMachine("Cam-01", config)
    
    # 模拟 60s 抓拍一次，且一直无人
    for i in range(6):
        print(f"--- 采样 {i+1} ---")
        # 模拟时间流逝 (这里强行修改内部时间加速测试)
        sm.window_start_time -= 60
        evt, status, mins, period = sm.update(has_person_this_frame=False)
        if evt:
            print(f"触发 MQTT 发送: {status}")

import threading
import queue
import time
import requests
import base64
import os

class GemmaReviewQueue:
    """
    文档 5.5 Gemma 复核门控与排队策略
    单例模式，全局唯一的复核队列，限制最大并发数为 1 (默认)。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(GemmaReviewQueue, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self, config=None):
        if self._initialized:
            return
            
        config = config or {}
        # 强制队列并发上限
        self.concurrency = config.get("gemma_review_queue_concurrency", 1)
        # 获取 Gemma API 地址。
        # 重要：如果 AI 引擎运行在宿主机，直接访问 127.0.0.1。
        # 如果在 Docker 容器内，则使用 host.docker.internal。
        default_gemma_host = "127.0.0.1"
        if os.path.exists("/.dockerenv"):
            default_gemma_host = "host.docker.internal"
            
        # 获取基础 URL 并统一到 OpenAI 兼容的 v1/chat/completions 接口
        raw_api_url = config.get("gemma_api_url", f"http://{default_gemma_host}:8080/completion")
        self.base_url = raw_api_url.split("/completion")[0].split("/v1")[0].rstrip("/")
        
        self.gemma_url = f"{self.base_url}/v1/chat/completions"
        self.gemma_slots_url = f"{self.base_url}/slots/0"
        
        # 强制检查：如果在宿主机运行但配置里写了 host.docker.internal，则修正它
        if not os.path.exists("/.dockerenv") and "host.docker.internal" in self.base_url:
            self.base_url = self.base_url.replace("host.docker.internal", "127.0.0.1")
            self.gemma_url = f"{self.base_url}/v1/chat/completions"
            self.gemma_slots_url = f"{self.base_url}/slots/0"
        
        # 优先级队列 (PriorityQueue)，优先级数字越小越先执行
        self.task_queue = queue.PriorityQueue(maxsize=10) # 限制最大积压10个任务，超出的直接降级丢弃
        
        # 启动消费线程
        self.workers = []
        for i in range(self.concurrency):
            t = threading.Thread(target=self._worker_loop, name=f"Gemma-Worker-{i}", daemon=True)
            t.start()
            self.workers.append(t)
            
        self._initialized = True
        print(f"✅ Gemma 复核队列初始化完成 (并发限制: {self.concurrency})")

    def _worker_loop(self):
        """后台线程不断从队列取任务去请求 Gemma"""
        while True:
            try:
                # 阻塞获取任务
                priority, timestamp, task = self.task_queue.get()
                
                # 如果任务排队太久 (比如超过了 30秒)，说明系统过载，直接丢弃该复核任务，执行降级策略
                if time.time() - timestamp > 30.0:
                    print(f"⚠️ Gemma 队列积压严重，任务 {task['id']} 已超时，执行默认降级")
                    task['result_event'].set() # 唤醒等待的线程，返回 None
                    self.task_queue.task_done()
                    continue
                    
                # 真正调用大模型
                result = self._call_gemma_api(task['jpg_bytes'], task['prompt'])
                
                # 回写结果并唤醒调用方
                task['result'] = result
                task['result_event'].set()
                
                self.task_queue.task_done()
                
            except Exception as e:
                print(f"❌ Gemma Worker 异常: {e}")
                time.sleep(1)

    def _call_gemma_api(self, jpg_bytes, prompt):
        """实际发起 HTTP 请求到本地 llama.cpp 部署的 Gemma 服务，带重试机制"""
        max_retries = 3
        retry_delay = 5  # 5秒重试间隔，适合处理模型重启场景
        
        last_error = ""
        for attempt in range(max_retries):
            try:
                # 1. 尝试清理 Slot 缓存 (兼容新旧 API)
                try:
                    # 优先尝试新版 API (POST with action=release)
                    requests.post(f"{self.gemma_slots_url}?action=release", timeout=0.5)
                except:
                    pass
                    
                # 2. 图像转 Base64
                img_b64 = base64.b64encode(jpg_bytes).decode('utf-8')
                img_url = f"data:image/jpeg;base64,{img_b64}"
                
                # 3. 构造消息体
                system_prompt = (
                    "You are a professional image analyzer. You MUST output a JSON object ONLY. "
                    "Structure: {\"result\": \"YES\" or \"NO\", \"analysis\": \"brief description\"}"
                )
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": img_url}},
                            {"type": "text", "text": f"{prompt}"}
                        ]
                    }
                ]
                
                payload = {
                    "model": "buildingos_review_engine",
                    "messages": messages,
                    "chat_template_kwargs": {"enable_thinking": False},
                    "temperature": 0.0,
                    "max_tokens": 256, 
                    "stream": False,
                    "stop": ["<end_of_turn>", "<eos>"]
                }
                
                # 4. 发起请求
                resp = requests.post(self.gemma_url, json=payload, timeout=15.0)
                
                if resp.status_code == 200:
                    data = resp.json()
                    msg = data.get('choices', [{}])[0].get('message', {})
                    content = msg.get('content', '').strip()
                    
                    import json
                    try:
                        clean_content = content.replace("```json", "").replace("```", "").strip()
                        res_json = json.loads(clean_content)
                        raw_result = str(res_json.get("result", "UNKNOWN")).upper()
                        analysis = res_json.get("analysis", "")
                        
                        final_res = "UNKNOWN"
                        if "YES" in raw_result: final_res = "YES"
                        elif "NO" in raw_result: final_res = "NO"
                        
                        return {
                            "result": final_res,
                            "prompt": prompt,
                            "llm_response": content,
                            "reasoning": analysis,
                            "retries": attempt
                        }
                    except Exception as je:
                        print(f"⚠️ Gemma JSON 解析失败: {je}, Content: {content}")
                        final_res = "UNKNOWN"
                        if "YES" in content.upper()[:50]: final_res = "YES"
                        elif "NO" in content.upper()[:50]: final_res = "NO"
                        
                        return {
                            "result": final_res,
                            "prompt": prompt,
                            "llm_response": content,
                            "reasoning": "JSON Parse Error",
                            "retries": attempt
                        }
                else:
                    last_error = f"HTTP {resp.status_code}"
                    print(f"❌ Gemma API 状态码异常: {resp.status_code} (尝试 {attempt+1}/{max_retries})")
            
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    print(f"⚠️ Gemma 连接错误 (尝试 {attempt+1}/{max_retries}): {e}。{retry_delay}s 后重试...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Gemma 重试耗尽，最终失败: {e}")
            except Exception as e:
                last_error = str(e)
                print(f"❌ Gemma 调用过程中发生非预期崩溃: {e}")
                break # 其他异常直接退出循环
                
        # 所有重试均失败
        return { 
            "result": "UNKNOWN", 
            "prompt": prompt, 
            "llm_response": last_error, 
            "reasoning": "All retries failed",
            "retries": max_retries - 1
        }

    def submit_review(self, task_id, task_type, jpg_bytes, prompt, yolo_conf=1.0):
        """
        提交复核任务并阻塞等待结果。
        """
        priority = 3
        if task_type == 'presence':
            if yolo_conf < 0.2:
                priority = 1
            elif yolo_conf < 0.4:
                priority = 2
        elif task_type == 'smoking':
            priority = 4

        task = {
            'id': task_id,
            'jpg_bytes': jpg_bytes,
            'prompt': prompt,
            'result': None,
            'result_event': threading.Event()
        }

        try:
            self.task_queue.put_nowait((priority, time.time(), task))
        except queue.Full:
            print(f"⚠️ Gemma 队列已满，直接拒绝任务 {task_id}")
            return { "result": "UNKNOWN", "prompt": prompt, "llm_response": "Queue Full", "reasoning": "", "retries": 0 }

        # 阻塞等待结果 (增加超时时间以容纳内部重试)
        waited = task['result_event'].wait(timeout=60.0)
        
        if not waited or task['result'] is None:
            print(f"⚠️ 任务 {task_id} 等待结果超时")
            return { "result": "UNKNOWN", "prompt": prompt, "llm_response": "Wait Timeout", "reasoning": "", "retries": 0 }
            
        return task['result']

# 全局单例实例
gemma_queue = GemmaReviewQueue()

import cv2
import threading
import time
import os
import json
import urllib.request
import urllib.parse
import base64
import numpy as np
from datetime import datetime
import paho.mqtt.client as mqtt
from flask import Flask, request, jsonify

# 导入我们新写的双轨制底层驱动与业务大脑
from yolo_infer import YoloTensorRTEngine
from rfdetr_trt_infer import RFDETRTensorRTEngine
from state_machine import PresenceStateMachine, SmokingStateMachine
from gemma_queue import gemma_queue
import paho.mqtt.client as mqtt

# --- Flask App for Single Image Test ---
flask_app = Flask(__name__)

@flask_app.route('/predict', methods=['POST'])
def api_predict():
    """
    接收 Base64 图片和参数，执行 AI 推理并返回结果。
    用于前端“测试图”功能，支持实时调整参数。
    """
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({"error": "No image data provided"}), 400
        
        # 1. 解码图片
        img_b64 = data['image']
        if ',' in img_b64:
            img_b64 = img_b64.split(',')[1]
        
        img_bytes = base64.b64decode(img_b64)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Failed to decode image"}), 400
        
        # 2. 获取参数
        conf_thres = data.get('conf_thres')
        if conf_thres is not None:
            conf_thres = float(conf_thres)
            
        # 3. 执行推理 (确保模型已初始化)
        init_tensorrt_models()
        
        # 默认使用人员感知模型 (RF-DETR 或 YOLO)
        results = []
        if pose_model:
            results = pose_model.predict(frame, conf_thres=conf_thres)
            
        # 4. 绘制结果图 (用于直观观测)
        annotated_frame = frame.copy()
        for res in results:
            x1, y1, x2, y2 = res['bbox']
            conf = res['conf']
            cls_id = res['class_id']
            # 获取类别名
            cls_name = "person" if cls_id == 0 else f"cls_{cls_id}"
            if hasattr(pose_model, 'classes') and cls_id < len(pose_model.classes):
                cls_name = pose_model.classes[cls_id]
                
            color = (0, 0, 255) if cls_id == 0 else (255, 0, 0)
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(annotated_frame, f"{cls_name} {conf:.2f}", (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
        # 5. 编码结果图为 Base64
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "results": results,
            "annotated_image": f"data:image/jpeg;base64,{annotated_b64}",
            "detector_source": presence_detector_source
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def run_flask():
    log_info("Starting Flask API server for AI testing on port 5000...")
    flask_app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# --- Environment Detection & Path/URL Translation Helpers ---
def is_in_container():
    return os.path.exists("/.dockerenv")

def get_real_path(p):
    """
    自适应路径转换：
    如果检测到不在容器内运行 (没有 /.dockerenv)，
    则将容器内的标准路径 /app/... 映射到宿主机的物理路径。
    """
    if is_in_container():
        return p
    
    # 获取宿主机项目根目录 (假设在 ~/buildingos.vision)
    home = os.path.expanduser("~")
    project_root = os.path.join(home, "buildingos.vision")
    
    if p.startswith("/app/www"):
        return p.replace("/app/www", os.path.join(project_root, "zlm/www"))
    if p.startswith("/app/models"):
        return p.replace("/app/models", os.path.join(project_root, "ai_engine/models"))
    if p.startswith("/app/ai_engine/config"):
        return p.replace("/app/ai_engine/config", os.path.join(project_root, "ai_engine/config"))
    if p.startswith("/app/"):
        # 通用映射：将容器根目录映射到宿主机的 ai_engine 目录
        return p.replace("/app/", os.path.join(project_root, "ai_engine/"))
    return p

def get_real_url(url, zlm_http_port=10081):
    """
    自适应 URL 转换：
    如果在宿主机运行，将容器名 'zlm:80' 替换为 '127.0.0.1:10081'。
    """
    if is_in_container():
        return url
    
    # 替换 API URL
    if "zlm:80" in url:
        return url.replace("zlm:80", f"127.0.0.1:{zlm_http_port}")
    
    # 额外处理 rtsp 地址
    if "rtsp://zlm:554" in url:
        # 这里的 10554 是宿主机映射出的端口
        return url.replace("zlm:554", "127.0.0.1:10554")
        
    return url

# --- Load Configuration ---
CONFIG_PATH = os.getenv("CONFIG_PATH", get_real_path("/app/ai_engine/config/config.json"))
DEFAULT_CONFIG_PATH = get_real_path("/app/ai_engine/config/config.default.json")

def load_config():
    # --- 自动初始化配置文件机制 ---
    if not os.path.exists(CONFIG_PATH):
        print(f"Warning: {CONFIG_PATH} not found. Initializing from default config...")
        try:
            import shutil
            if os.path.exists(DEFAULT_CONFIG_PATH):
                shutil.copy(DEFAULT_CONFIG_PATH, CONFIG_PATH)
                print(f"Successfully copied {DEFAULT_CONFIG_PATH} to {CONFIG_PATH}")
            else:
                # 连 default 都找不到时的保底方案
                with open(CONFIG_PATH, 'w') as f:
                    json.dump({"streams": {"occupancy": [], "smoking": []}}, f, indent=4)
                print(f"Created empty config at {CONFIG_PATH}")
        except Exception as e:
            print(f"Error initializing config file: {e}")
            
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

config = load_config()

# --- Unified Camera Config Parser ---
def get_unified_cameras(cfg):
    """将旧版 streams.smoking 和 streams.occupancy 配置统一转换为 cameras 字典"""
    cameras = {}
    streams = cfg.get("streams", {})
    
    # 解析人员感知流 (Presence)
    for cam in streams.get("occupancy", []):
        cam_id = cam.get("id")
        if not cam_id: continue
        cameras[cam_id] = {
            "source_url": cam.get("source_url"),
            "url": get_real_url(cam.get("url"), config.get("ai_engine", {}).get("zlm_http_port", 10081)), # 需自适应
            "areaCode": cam.get("areaCode", "UNKNOWN"),
            "enabled": True,
            "tasks": ["presence"]
        }
        
    # 解析吸烟检测流 (Smoking)
    for cam in streams.get("smoking", []):
        cam_id = cam.get("id")
        if not cam_id: continue
        if cam_id in cameras:
            cameras[cam_id]["tasks"].append("smoking")
            if not cameras[cam_id].get("areaCode") or cameras[cam_id].get("areaCode") == "UNKNOWN":
                cameras[cam_id]["areaCode"] = cam.get("areaCode", "UNKNOWN")
        else:
            cameras[cam_id] = {
                "source_url": cam.get("source_url"),
                "url": get_real_url(cam.get("url"), config.get("ai_engine", {}).get("zlm_http_port", 10081)), # 需自适应
                "areaCode": cam.get("areaCode", "UNKNOWN"),
                "enabled": True,
                "tasks": ["smoking"]
            }
    return cameras

camera_config = get_unified_cameras(config)

# AI Engine specific configuration (与 ZLM 共用)
ai_config = config.get("ai_engine", {})
ZLM_HTTP_PORT = ai_config.get("zlm_http_port", 10081)
ZLM_RTSP_PORT = ai_config.get("zlm_rtsp_port", 10554)

# 从环境变量获取 API Secret，ZLM_API_SECRET 已经在 docker-compose 中统一定义
ZLM_API_SECRET = os.getenv("ZLM_API_SECRET", "buildingos_edge_secret_2026")

def log_info(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

# --- Global Dictionaries ---
presence_machines = {} # 存储每个摄像头的 Presence 状态机
smoking_machines = {}  # 存储每个摄像头的 Smoking 状态机
mqtt_cooldowns = {}    # MQTT 发送冷却时间戳 (去重键)

# 全局模型占位符 (延迟加载)
pose_model = None
smoking_model = None
presence_detector_source = "detector"

# 确保 TensorRT 初始化的锁，防止多个摄像头线程同时触发初始化
trt_init_lock = threading.Lock()

# --- Init TensorRT Engines ---
def init_tensorrt_models():
    global pose_model, smoking_model, presence_detector_source
    
    with trt_init_lock:
        if pose_model is not None and smoking_model is not None:
            return
            
        print("Initializing detection models...")
        try:
            detector_cfg = ai_config.get("detector", {})
            presence_backend = detector_cfg.get("presence_backend", "yolo").lower()
            presence_conf = float(detector_cfg.get("presence_conf", 0.25))
            fallback_yolo_path = get_real_path(detector_cfg.get("fallback_yolo_engine_path", "/app/models/yolo26m-pose.engine"))
            if presence_backend == "rfdetr_trt":
                try:
                    presence_engine_path = get_real_path(detector_cfg.get("presence_engine_path", "/app/models/rf-detr-fp16-576.engine"))
                    person_class_id = int(detector_cfg.get("person_class_id", 0))
                    max_det = int(detector_cfg.get("max_det", 100))
                    pose_model = RFDETRTensorRTEngine(
                        presence_engine_path,
                        conf_thres=presence_conf,
                        person_class_id=person_class_id,
                        max_det=max_det
                    )
                    presence_detector_source = "rf-detr"
                except Exception as e:
                    print(f"RF-DETR init failed, fallback to YOLO: {e}")
                    pose_model = YoloTensorRTEngine(fallback_yolo_path, conf_thres=presence_conf)
                    presence_detector_source = "yolo26m"
            else:
                presence_engine_path = get_real_path(detector_cfg.get("presence_engine_path", fallback_yolo_path))
                pose_model = YoloTensorRTEngine(presence_engine_path, conf_thres=presence_conf)
                presence_detector_source = "yolo26m"

            smoking_engine_path = get_real_path(detector_cfg.get("smoking_engine_path", "/app/models/smoking_26m.engine"))
            smoking_conf = float(detector_cfg.get("smoking_conf", 0.3))
            smoking_model = YoloTensorRTEngine(smoking_engine_path, conf_thres=smoking_conf)
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Failed to load TensorRT engines: {e}")
            print("Please check detector config and engine files")

# --- MQTT Setup ---
MQTT_BROKER = config.get("mqtt", {}).get("broker", "127.0.0.1")
# 如果在宿主机运行，且 broker 依然是容器名，则强制修正为 127.0.0.1
if not is_in_container() and "buildingos-emqx-prod" in MQTT_BROKER:
    MQTT_BROKER = "127.0.0.1"

MQTT_PORT = config.get("mqtt", {}).get("port", 1883)
MQTT_KEEPALIVE = 60

try:
    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
except AttributeError:
    # 兼容老版本 paho-mqtt
    mqtt_client = mqtt.Client()

try:
    print(f"Connecting to MQTT Broker at {MQTT_BROKER}:{MQTT_PORT}...")
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=MQTT_KEEPALIVE)
    mqtt_client.loop_start()
    print("✅ MQTT Connected.")
except Exception as e:
    print(f"❌ Error connecting to MQTT: {e}")
    if "[Errno 111]" in str(e):
        print("   💡 TIP: Connection refused. This usually means the MQTT Broker (EMQX/Mosquitto) is not running.")
        print("   💡 Try starting it: 'sudo systemctl start emqx' or 'sudo docker compose up -d' if using Docker.")
    print("   WARNING: AI Engine will continue to run without publishing events.")

def save_minute_log_for_frontend(cam_id, area_code, has_person, raw_payload=None, images=None, decision_chain=None, yolo_count=0, gemma_details=None, smoking_count=0, smoking_conf=0.0):
    """
    不管是否触发 MQTT 报警，每一分钟（或每一个采样周期）都将原始判定结果
    追加保存到本地的 JSON 中，以保证前端的 Heatmap 有细粒度的数据点。
    """
    if not cam_id or not area_code or area_code == "UNKNOWN":
        log_info(f"⚠️ 跳过保存无效日志: cam_id='{cam_id}', area_code='{area_code}'")
        return

    try:
        log_dir_base = get_real_path(config.get("storage_quota", {}).get("occupancy_log_dir", "/app/www/occupancy_logs"))
        today_str = datetime.now().strftime("%Y-%m-%d")
        safe_area = str(area_code).replace('/', '_').replace('\\', '_')
        target_dir = os.path.join(log_dir_base, today_str, safe_area)
        os.makedirs(target_dir, exist_ok=True)
        
        # 强制填充 decision_chain，防止前端显示“无日志”
        if not decision_chain:
            decision_chain = ["AI 引擎默认状态更新"]
        
        # 写入图片
        image_paths = []
        timestamp_ms = int(time.time() * 1000)
        
        # 修复 numpy truth value ambiguous 报错: 不要直接使用 `if images:`
        if isinstance(images, list) and len(images) > 0:
            for i, img in enumerate(images):
                if img is not None:
                    img_name = f"{cam_id}_sample_{timestamp_ms}_{i}.jpg"
                    img_path = os.path.join(target_dir, img_name)
                    cv2.imwrite(img_path, img)
                    rel_path = f"occupancy_logs/{today_str}/{safe_area}/{img_name}"
                    image_paths.append(rel_path)
        elif images is not None: # 直接用 is not None 检查 numpy array
            img_name = f"{cam_id}_sample_{timestamp_ms}.jpg"
            img_path = os.path.join(target_dir, img_name)
            cv2.imwrite(img_path, images)
            rel_path = f"occupancy_logs/{today_str}/{safe_area}/{img_name}"
            image_paths.append(rel_path)

        log_entry = {
            "id": f"{cam_id}_{timestamp_ms}",
            "date": today_str,
            "timestamp": datetime.now().isoformat(),
            "camera_id": cam_id,
            "areaCode": area_code,
            "event": "Presence Sample",
            "detector_type": "RF-DETR" if "rf-detr" in presence_detector_source else "YOLO",
            "threshold_used": "1-minute sample",
            "images": image_paths,
            "raw_payload": raw_payload or {
                "result": "occupied" if has_person else "empty",
                "source": f"{presence_detector_source}+gemma",
                "detector_type": "RF-DETR" if "rf-detr" in presence_detector_source else "YOLO",
                "decision_chain": decision_chain,
                "yolo_count": yolo_count,
                "smoking_count": smoking_count,
                "smoking_conf": smoking_conf
            }
        }
        
        if gemma_details:
            log_entry["gemma"] = gemma_details
        
        json_path = os.path.join(target_dir, f"{cam_id}_sample_{timestamp_ms}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, ensure_ascii=False, indent=4)
            
    except Exception as e:
        log_info(f"❌ 保存前端日志失败: {e}")

def publish_mqtt_event(cam_id, area_code, event_type, payload, frame=None):
    """带冷却去重机制的 MQTT 发布，同时持久化到本地日志供 Web 查阅"""
    # 强制去重键: areaCode/camera + eventType
    dedup_key = f"{area_code}_{cam_id}_{event_type}"
    now = time.time()
    
    # 强制冷却时间：180 秒 (3分钟)
    cooldown = config.get("mqtt_alert_cooldown_seconds", 180)
    
    if dedup_key in mqtt_cooldowns:
        if now - mqtt_cooldowns[dedup_key] < cooldown:
            print(f"[{cam_id}] MQTT {event_type} 在 {cooldown}s 冷却期内，跳过发送")
            return
            
    # 执行发送
    topic = "buildingos/presence/result" if event_type == "presence" else "buildingos/smoking/alert"
    try:
        mqtt_client.publish(topic, json.dumps(payload))
        mqtt_cooldowns[dedup_key] = now
        print(f"[{cam_id}] => MQTT 已发布 {topic}: {payload['result']}")
        
        # --- 本地持久化 (供 Web 界面场景检测结果展示) ---
        try:
            log_dir_base = get_real_path(config.get("storage_quota", {}).get("occupancy_log_dir", "/app/www/occupancy_logs"))
            today_str = datetime.now().strftime("%Y-%m-%d")
            # 清理 area_code 中的非法路径字符
            safe_area = str(area_code).replace('/', '_').replace('\\', '_')
            target_dir = os.path.join(log_dir_base, today_str, safe_area)
            os.makedirs(target_dir, exist_ok=True)
            
            timestamp_ms = int(now * 1000)
            
            # 1. 保存截图
            image_path = ""
            if frame is not None:
                img_name = f"{cam_id}_{event_type}_{timestamp_ms}.jpg"
                img_full_path = os.path.join(target_dir, img_name)
                cv2.imwrite(img_full_path, frame)
                # 记录相对路径，Web 端会自动拼接 ZLM 端口
                image_path = f"occupancy_logs/{today_str}/{safe_area}/{img_name}"
            
            # 2. 构造日志结构 (兼容旧版 UI)
            log_entry = {
                "event": "Smoking Alert" if event_type == "smoking" else "Presence Update",
                "areaCode": area_code,
                "detector_type": "RF-DETR" if (event_type == "presence" and "rf-detr" in presence_detector_source) else "YOLO",
                "is_occupied": payload.get("result") == "occupied" or payload.get("result") == "confirmed_smoking",
                "person_count": 1 if payload.get("result") in ["occupied", "confirmed_smoking"] else 0,
                "timestamp": payload.get("timestamp"),
                "scores": {
                    "visual": payload.get("windowMinutes", 0),
                    "total": 1.0,
                    "time_bias": payload.get("sampleIntervalSeconds", 0)
                },
                "threshold_used": "Gemma E2B Verified",
                "images": [image_path] if image_path else [],
                "raw_payload": payload
            }
            
            # 3. 保存 JSON
            json_path = os.path.join(target_dir, f"{cam_id}_{event_type}_{timestamp_ms}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[{cam_id}] 本地日志持久化失败: {e}")

    except Exception as e:
        print(f"[{cam_id}] MQTT 发送失败: {e}")

# --- Camera Processing Thread (每 60s/20s 抓拍) ---
import subprocess
import random

# --- Host FFmpeg Snapshot Helper ---
def get_frame_from_host_ffmpeg(cam_id):
    """
    直接在宿主机调用 ffmpeg 进程抓取 ZLM 转发的 RTSP 流。
    这种方式无状态、无缓存，且强制使用 TCP 传输，能保证 100% 画面完整。
    """
    # 宿主机上 ZLM 转发的 RTSP 地址
    local_rtsp_url = f"rtsp://127.0.0.1:{ZLM_RTSP_PORT}/live/{cam_id}"
    tmp_snap_path = f"/tmp/snap_{cam_id}_{int(time.time())}.jpg"
    
    # 构造 ffmpeg 命令
    # -rtsp_transport tcp: 强制使用 TCP，防止 UDP 丢包导致花屏
    # -y: 覆盖输出文件
    # -i: 输入流
    # -frames:v 1: 只截取一帧
    # -f image2: 输出格式为图片
    # 注意：FFmpeg 必须已安装在宿主机 PATH 中
    cmd = [
        "ffmpeg", 
        "-rtsp_transport", "tcp", 
        "-y", 
        "-i", local_rtsp_url, 
        "-frames:v", "1", 
        "-f", "image2", 
        tmp_snap_path
    ]
    
    try:
        # 执行抓拍，设置 15 秒超时防止卡死
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)
        
        if result.returncode == 0 and os.path.exists(tmp_snap_path):
            frame = cv2.imread(tmp_snap_path)
            # 及时清理临时文件
            try:
                os.remove(tmp_snap_path)
            except:
                pass
            return frame
        else:
            log_info(f"[{cam_id}] FFmpeg 抓拍失败: {result.stderr.decode() if result.stderr else 'Unknown error'}")
            return None
    except subprocess.TimeoutExpired:
        log_info(f"[{cam_id}] FFmpeg 抓拍超时 (15s)")
        return None
    except Exception as e:
        log_info(f"[{cam_id}] FFmpeg 抓拍异常: {e}")
        return None

def process_camera(cam_id, cam_info):
    """
    针对每个摄像头运行的独立采样线程。
    核心逻辑：使用宿主机 FFmpeg 进行定时无状态抓拍。
    """
    global presence_detector_source
    
    area_code = cam_info.get("areaCode", "UNKNOWN")
    enabled = cam_info.get("enabled", True)

    if not enabled:
        log_info(f"[{cam_id}] Camera is disabled in config.")
        return

    log_info(f"[{cam_id}] Starting host-ffmpeg sampling thread...")

    # 初始化状态机
    if cam_id not in presence_machines:
        presence_machines[cam_id] = PresenceStateMachine(cam_id, config)
    if cam_id not in smoking_machines:
        smoking_machines[cam_id] = SmokingStateMachine(cam_id, config)
        
    p_sm = presence_machines[cam_id]
    s_sm = smoking_machines[cam_id]
    
    tasks = cam_info.get("tasks", [])
    has_presence_task = "presence" in tasks
    has_smoking_task = "smoking" in tasks

    # 抓拍间隔配置
    p_interval = config.get("presence_sample_interval_seconds", 60)
    s_interval = config.get("smoke_sample_interval_seconds", 20)
    
    # 错峰采样延迟，防止并发调用 ffmpeg 进程导致 CPU 瞬间爆表
    stagger_delay = random.uniform(0, 5)
    log_info(f"[{cam_id}] 采样错峰延迟: {stagger_delay:.2f}s")
    time.sleep(stagger_delay)

    last_p_time = 0
    last_s_time = 0

    while True:
        try:
            now = time.time()
            need_p_sample = has_presence_task and (now - last_p_time) >= p_interval
            
            # Smoking 逻辑修改：不再受窗口限制，只要有任务且满足基础间隔，或者随动于 Presence 采样
            # 基础采样逻辑：如果有人感应任务，我们就随动；如果没有人感应只有吸烟，则按吸烟间隔跑
            if has_presence_task:
                need_s_sample = has_smoking_task and need_p_sample
            else:
                need_s_sample = has_smoking_task and (now - last_s_time) >= s_interval

            if need_p_sample or need_s_sample:
                # 使用宿主机本地 FFmpeg 抓拍
                frame = get_frame_from_host_ffmpeg(cam_id)
                
                if frame is None:
                    time.sleep(5)
                    continue
                
                # 预热初始化 TensorRT (如果是首次)
                init_tensorrt_models()
                
                has_person = False
                s_count = 0
                max_s_conf = 0.0
                decision_chain = []
                yolo_count = 0
                annotated_frame = frame.copy()
                gemma_details = None

                # --- 1. Presence (人员存在) 综合判定流程 ---
                if need_p_sample:
                    last_p_time = now
                    
                    # 确定当前检测器名称
                    current_detector = "RF-DETR" if "rf-detr" in presence_detector_source else "YOLO"
                    
                    # RF-DETR/YOLO 一级判定
                    boxes = pose_model.predict(frame)
                    
                    # 过滤出“人”类别的框 (person_class_id 通常是 0)
                    person_boxes = [b for b in boxes if b.get('class_id') == 0]
                    
                    yolo_count = len(person_boxes)
                    
                    # 绘制时间戳
                    cv2.putText(annotated_frame, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # 绘制所有检测到的目标（用于调试分析）
                    if len(boxes) > 0:
                        for b in boxes:
                            x1, y1, x2, y2 = b['bbox']
                            cls_name = b.get('class_name', 'unknown')
                            conf = b['conf']
                            # 人用红色，其他用蓝色
                            color = (0, 0, 255) if cls_name == 'person' else (255, 0, 0)
                            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(annotated_frame, f"{cls_name} {conf:.2f}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
                    if yolo_count > 0:
                        decision_chain.append(f"{current_detector} 检测到 {yolo_count} 个候选人员")
                        max_conf = max([b['conf'] for b in person_boxes])
                    else:
                        decision_chain.append(f"{current_detector} 未检测到人员，准备全图复核")
                        max_conf = 0.0

                    # --- 核心改进逻辑 ---
                    # 1. 如果 Detector 信心极高 (>= 70%)，直接通过，不麻烦 Gemma
                    if max_conf >= 0.70:
                        gemma_res = "YES"
                        decision_chain.append(f"{current_detector} 高置信度({max_conf:.2f})直接确认有人")
                    else:
                        # 2. 否则，送给 Gemma 做最终裁决
                        prompt = "检测图片中是否有活人存在，仔细鉴别头肩和肢体等人体要输，如果有人回答YES，并且告知在什么位置。没有则回答NO"
                        success, buffer = cv2.imencode('.jpg', frame)
                        if success:
                            jpg_bytes = buffer.tobytes()
                            # submit_review 现在返回 dict {result, prompt, llm_response, reasoning, retries}
                            gemma_data = gemma_queue.submit_review(f"{cam_id}_P_{now}", "presence", jpg_bytes, prompt, yolo_conf=max_conf)
                            gemma_res = gemma_data.get("result", "UNKNOWN")
                            gemma_details = gemma_data
                            retries = gemma_data.get("retries", 0)
                            
                            if gemma_res == "UNKNOWN":
                                # 异常降级保护：如果所有重试均失败
                                hour = datetime.now().hour
                                is_worktime = 9 <= hour < 19
                                
                                retry_info = f" (重试 {retries} 次失败)" if retries > 0 else ""
                                
                                if yolo_count > 0:
                                    if is_worktime:
                                        gemma_res = "YES"
                                        decision_chain.append(f"Gemma 响应异常{retry_info}，上班时段采信 Detector: YES")
                                    else:
                                        gemma_res = "NO"
                                        decision_chain.append(f"Gemma 响应异常{retry_info}，非上班时段强制判定: NO")
                                else:
                                    gemma_res = "NO"
                                    decision_chain.append(f"Gemma 响应异常{retry_info}，且未发现目标，判定: NO")
                            else:
                                retry_suffix = f" (重试 {retries} 次成功)" if retries > 0 else ""
                                decision_chain.append(f"Gemma 二级裁决结果: {gemma_res}{retry_suffix}")
                        else:
                            log_info(f"[{cam_id}] OpenCV JPEG 编码失败，降级采信 Detector")
                            gemma_res = "YES" if yolo_count > 0 else "NO"
                            decision_chain.append("图像编码失败，降级采信 Detector")
                            gemma_details = None
                    
                    if gemma_res == "YES":
                        has_person = True
                        if max_conf < 0.70:
                            if yolo_count > 0:
                                decision_chain.append("Gemma 复核: 确认图中存在真实人员")
                            else:
                                decision_chain.append("Gemma 复核: Detector漏报，但Gemma在全图中发现了人员")
                        log_info(f"[{cam_id}] Presence: 确认有人 (YOLO框: {yolo_count}个, MaxConf: {max_conf:.2f})")
                    else:
                        has_person = False # 确保明确赋值
                        if yolo_count > 0:
                            decision_chain.append("Gemma 复核: 否决 (认定疑似目标为误报/假人)")
                        else:
                            decision_chain.append("Gemma 复核: 确认全图确实无人")
                        log_info(f"[{cam_id}] Presence: 判定无人")
                    
                    # 无论有没有人，送入状态机处理时间窗口
                    event_triggered, final_status, window_mins, time_period = p_sm.update(has_person_this_frame=has_person)
                    
                    # 如果状态机决定收敛，触发 MQTT
                    if event_triggered:
                        payload = {
                            "areaCode": area_code,
                            "result": final_status, # occupied / empty
                            "windowMinutes": window_mins,
                            "timePeriod": time_period,
                            "source": f"{presence_detector_source}+gemma",
                            "detector_type": "RF-DETR" if "rf-detr" in presence_detector_source else "YOLO",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # 【核心优化】发布报警时，也使用标注过的图作为证据
                        publish_mqtt_event(cam_id, area_code, "presence", payload, annotated_frame)

                # --- 2. Smoking (吸烟检测) 随动判定流程 ---
                if has_smoking_task and (not has_presence_task or has_person) and smoking_model:
                    last_s_time = now # 更新采样时间
                    # 只要本轮满足条件，立即调用吸烟模型
                    s_boxes = smoking_model.predict(frame)
                    s_count = len(s_boxes)
                    
                    if s_count > 0:
                        max_s_conf = max([b['conf'] for b in s_boxes])
                        log_info(f"[{cam_id}] Smoking: 检测到疑似吸烟目标! (数量: {s_count}, MaxConf: {max_s_conf:.2f})")
                        s_sm.confirm_smoke()
                    else:
                        log_info(f"[{cam_id}] Smoking: 区域有人但未发现吸烟动作。")

                # --- 3. 记录日志 (不管是否采样人感，只要有采样就记录) ---
                if need_p_sample or need_s_sample:
                    save_minute_log_for_frontend(
                        cam_id, 
                        area_code, 
                        has_person, 
                        images=[annotated_frame, frame], 
                        decision_chain=decision_chain, 
                        yolo_count=yolo_count,
                        gemma_details=gemma_details,
                        smoking_count=s_count,
                        smoking_conf=max_s_conf
                    )

            # 休眠 1 秒，防止死循环跑满 CPU
            time.sleep(1)

        except Exception as e:
            print(f"[{cam_id}] 线程发生严重异常: {e}")
            time.sleep(5)

# --- ZLMediaKit Auto-Proxy Setup ---
def register_cameras_to_zlm():
    print("Waiting for ZLMediaKit to start...")
    # 把等待时间拉长，因为容器启动有先后，ZLM 可能还没就绪
    time.sleep(10) 
    
    # 获取 ZLM API 根路径
    zlm_api_root = get_real_url(config.get("zlm", {}).get("api_url", "http://zlm:80/index/api"), ZLM_HTTP_PORT)
    if not zlm_api_root.endswith("/addStreamProxy"):
        api_url = f"{zlm_api_root.rstrip('/')}/addStreamProxy"
    else:
        api_url = zlm_api_root

    # 为每个摄像头创建一个独立的注册重试逻辑
    def register_single_cam(cam_id, cam_info):
        rtsp_source = cam_info.get("source_url")
        if not rtsp_source:
            # 兼容处理：尝试从 config 原始数据里捞
            for stream_type in ["smoking", "occupancy"]:
                for stream in config.get("streams", {}).get(stream_type, []):
                    if stream.get("id") == cam_id:
                        rtsp_source = stream.get("source_url")
                        break
                if rtsp_source: break
        
        if not rtsp_source:
            print(f"[{cam_id}] Cannot find physical source_url for ZLM proxy. Skipping.")
            return
            
        if not cam_info.get("enabled", True):
            return

        params = {
            "secret": ZLM_API_SECRET,
            "vhost": "__defaultVhost__",
            "app": "live",
            "stream": cam_id,
            "url": rtsp_source,
            "enable_rtmp": 1,
            "enable_rtsp": 1,
            "enable_hls": 1,
            "enable_mp4": 0
        }
        query_string = urllib.parse.urlencode(params)
        full_url = f"{api_url}?{query_string}"

        retry_count = 0
        while True:
            try:
                req = urllib.request.Request(full_url, method="POST")
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode())
                    if res_data.get("code") == 0:
                        play_url = get_real_url(f"rtsp://zlm:554/live/{cam_id}")
                        print(f"[{cam_id}] ZLM Proxy configured successfully. Live at {play_url}")
                        break
                    elif "already exists" in res_data.get("msg", ""):
                        print(f"[{cam_id}] ZLM Proxy already exists. Skipping.")
                        break
                    else:
                        print(f"[{cam_id}] ZLM Proxy failed: {res_data.get('msg')}. Retrying in 30s...")
            except Exception as e:
                print(f"[{cam_id}] Connection to ZLM API failed: {e}. Retrying in 30s...")
            
            retry_count += 1
            time.sleep(30) # 失败后每 30 秒重试一次

    # 启动多个线程并行处理每个摄像头的注册，防止一个摄像头卡住影响全局
    reg_threads = []
    for cam_id, cam_info in camera_config.items():
        t = threading.Thread(target=register_single_cam, args=(cam_id, cam_info), daemon=True)
        t.start()
        reg_threads.append(t)

# --- Main Entry Point ---
if __name__ == "__main__":
    print("Starting AI Engine (Dual-Stage Architecture)...")
    
    # 检查 ffmpeg 是否存在，防止后续抓拍静默失败
    import shutil
    if not shutil.which("ffmpeg"):
        print("\n" + "!"*60)
        print("CRITICAL ERROR: 'ffmpeg' not found in system PATH!")
        print("This AI Engine requires FFmpeg to capture snapshots from RTSP streams.")
        print("Please follow the setup guide in docs/cicd.md to install it:")
        print("  sudo apt-get update && sudo apt-get install -y ffmpeg")
        print("!"*60 + "\n")
    
    # 注册 ZLM 代理 (项目核心记忆: 动态拉流)
    zlm_thread = threading.Thread(target=register_cameras_to_zlm)
    zlm_thread.start()

    # 重点：为了彻底消除多线程并发初始化导致的 double free，
    # 我们在主线程中先行预热初始化 TensorRT，然后再开启各个摄像头的处理线程。
    # 这样所有的 OpenCV GStreamer 实例化都会发生在模型加载完毕之后，避免内存抢占。
    # 由于需要连接视频流，这里我们可以做个短暂的等待，或者直接在主线程加载。
    print("Pre-loading TensorRT Engines sequentially in main thread...")
    init_tensorrt_models()

    # 启动摄像头定时采样线程
    threads = []
    
    # 启动单图测试 HTTP 服务
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    for cam_id, cam_info in camera_config.items():
        t = threading.Thread(target=process_camera, args=(cam_id, cam_info))
        t.start()
        threads.append(t)

    # 保持主线程运行
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down AI Engine...")
        mqtt_client.loop_stop()
        os._exit(0)

```

## 后30页
以下为后30页的连续源代码片段（Web管理前端与后端服务）。

```
const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const os = require('os');
const http = require('http');

const app = express();
const server = http.createServer(app);

// WebSocket setup for real-time logs
const { Server } = require("socket.io");
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

app.use(cors());
app.use(express.json({ limit: '20mb' }));
app.use(express.urlencoded({ limit: '20mb', extended: true }));

// Docker 容器内的挂载路径
const CONFIG_PATH = '/app/ai_engine/config/config.json';
const DEFAULT_CONFIG_PATH = '/app/ai_engine/config/config.default.json';
const PROJECT_DIR = '/host_project';
const HOST_NSENTER = 'nsenter -t 1 -m -u -i -n -p --';

// --- 自动初始化配置文件机制 ---
if (!fs.existsSync(CONFIG_PATH)) {
    console.log(`Warning: ${CONFIG_PATH} not found. Initializing from default config...`);
    try {
        if (fs.existsSync(DEFAULT_CONFIG_PATH)) {
            fs.copyFileSync(DEFAULT_CONFIG_PATH, CONFIG_PATH);
            console.log(`Successfully copied ${DEFAULT_CONFIG_PATH} to ${CONFIG_PATH}`);
        } else {
            // 保底方案
            const emptyConfig = { streams: { occupancy: [], smoking: [] } };
            fs.writeFileSync(CONFIG_PATH, JSON.stringify(emptyConfig, null, 4), 'utf8');
            console.log(`Created empty config at ${CONFIG_PATH}`);
        }
    } catch (e) {
        console.error(`Error initializing config file: ${e.message}`);
    }
}

// Real-time AI Logs via Docker logs
let logProcess = null;

io.on('connection', (socket) => {
    console.log('Client connected for AI logs');
    
    // Send a welcome message
    socket.emit('log', { timestamp: new Date().toISOString(), message: 'Connected to AI Engine log stream...' });

    if (!logProcess) {
        // Spawn a process to tail docker logs
        // Using stdbuf or unbuffer might be needed depending on system, but tail -f usually works
        logProcess = exec(`${HOST_NSENTER} journalctl -u ai-engine -f -n 200 --no-pager`);
        
        logProcess.stdout.on('data', (data) => {
            const lines = data.split('\n');
            lines.forEach(line => {
                if (line.trim()) {
                    // Very simple parsing, try to extract camera ID if present [cam_id]
                    let camId = 'system';
                    const match = line.match(/\[(.*?)\]/);
                    if (match && match[1]) {
                        camId = match[1];
                    }
                    
                    io.emit('log', {
                        timestamp: new Date().toISOString(),
                        message: line,
                        camId: camId
                    });
                }
            });
        });

        logProcess.stderr.on('data', (data) => {
             const lines = data.split('\n');
             lines.forEach(line => {
                 if (line.trim()) {
                     io.emit('log', {
                         timestamp: new Date().toISOString(),
                         message: `[ERROR] ${line}`,
                         camId: 'system'
                     });
                 }
             });
        });
    }

    socket.on('disconnect', () => {
        console.log('Client disconnected from logs');
        // If no more clients, maybe kill logProcess, but it's fine to keep running for a small edge device
    });
});

// --- 1. 系统状态与登录 API ---
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    try {
        const config = fs.existsSync(CONFIG_PATH) ? JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')) : {};
        const auth = config.auth || { admin: 'admin', password: 'admin' };
        
        if (username === auth.admin && password === auth.password) {
            // Simple mock token
            res.json({ status: 'ok', token: 'buildingos_token_2026', username: auth.admin });
        } else {
            res.status(401).json({ status: 'error', message: 'Invalid username or password' });
        }
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/ping', (req, res) => {
    res.json({ status: 'ok', message: 'System is running' });
});

app.get('/api/system/info', (req, res) => {
    try {
        // 1. 获取存储空间信息 (始终执行)
        let diskInfo = { used: 0, total: 0, percent: 0 };
        try {
            // 优先检测 /app/www (容器内存储路径)
            const checkPaths = ['/app/www', '/host_project', '/'];
            let found = false;
            for (const p of checkPaths) {
                if (fs.existsSync(p)) {
                    try {
                        // 尝试使用 statfsSync
                        const stats = fs.statfsSync(p);
                        diskInfo.total = Number(stats.bsize) * Number(stats.blocks);
                        diskInfo.used = diskInfo.total - (Number(stats.bsize) * Number(stats.bfree));
                        if (diskInfo.total > 0) {
                            diskInfo.percent = (diskInfo.used / diskInfo.total) * 100;
                            found = true;
                            break;
                        }
                    } catch (e) {
                        // 如果 statfsSync 失败，尝试 df 命令
                        const dfOut = require('child_process').execSync(`df -B1 ${p} | tail -1`).toString();
                        const parts = dfOut.trim().split(/\s+/);
                        if (parts.length >= 4) {
                            diskInfo.total = parseInt(parts[1]);
                            diskInfo.used = parseInt(parts[2]);
                            diskInfo.percent = (diskInfo.used / diskInfo.total) * 100;
                            found = true;
                            break;
                        }
                    }
                }
            }
        } catch (diskErr) {
            console.warn("Failed to fetch disk info:", diskErr);
        }

        const jtopFiles = ['/host_tmp/jtop_status.json', '/tmp/jtop_status.json'];
        const jtopFile = jtopFiles.find(file => fs.existsSync(file));
        if (jtopFile) {
            try {
                const jtopData = JSON.parse(fs.readFileSync(jtopFile, 'utf8'));
                if (!jtopData.error) {
                    // 将磁盘信息合并到 jtop 数据中返回
                    jtopData.disk = diskInfo;
                    return res.json(jtopData);
                }
            } catch (e) {
                console.warn("Failed to read jtop file:", e);
            }
        }
        
        // Fallback 逻辑
        const totalMem = os.totalmem();
        const freeMem = os.freemem();
        const usedMem = totalMem - freeMem;
        const memUsage = (usedMem / totalMem) * 100;
        
        const cpus = os.cpus();

        exec('nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits', (smiErr, smiOut) => {
            let gpuInfo = { util: 0, memUsed: 0, memTotal: 0 };
            if (!smiErr && smiOut) {
                const parts = smiOut.split(',').map(s => s.trim());
                if (parts.length >= 3) {
                    gpuInfo = {
                        util: parseFloat(parts[0]),
                        memUsed: parseFloat(parts[1]),
                        memTotal: parseFloat(parts[2])
                    };
                }
            }
            
            res.json({
                cpu: {
                    usage: Math.random() * 100, // Mock for fallback
                    cores: cpus.length,
                    details: {}
                },
                memory: {
                    ram: {
                        usagePercent: memUsage,
                        used: usedMem,
                        total: totalMem
                    },
                    swap: { usagePercent: 0, used: 0, total: 0 }
                },
                gpu: gpuInfo,
                disk: diskInfo,
                engines: {},
                power: { total: 0, gpu: 0, cpu: 0 },
                temperature: {},
                board: {
                    model: 'Fallback System',
                    jetpack: 'N/A',
                    nvpmodel: 'N/A',
                    uptime: os.uptime()
                }
            });
        });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/zlm/metrics', (req, res) => {
    try {
        const config = fs.existsSync(CONFIG_PATH) ? JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')) : {};
        const zlmSecret = process.env.ZLM_API_SECRET || config.zlm?.secret || "buildingos_edge_secret_2026";
        const getMediaListUrl = `http://zlm:80/index/api/getMediaList?secret=${zlmSecret}`;
        
        http.get(getMediaListUrl, (zlmRes) => {
            let data = '';
            zlmRes.on('data', (chunk) => {
                data += chunk;
            });
            zlmRes.on('end', () => {
                try {
                    const zlmResponse = JSON.parse(data);
                    res.json(zlmResponse);
                } catch (e) {
                    console.error("Parse ZLM response failed:", e, data);
                    res.status(500).json({ error: "Failed to parse ZLM response" });
                }
            });
        }).on('error', (err) => {
            console.error("HTTP GET to ZLM failed:", err);
            res.status(500).json({ error: "Failed to fetch ZLM data" });
        });
    } catch (e) {
        console.error("ZLM Metrics API Error:", e);
        res.status(500).json({ error: e.message });
    }
});

app.post('/api/system/reboot', (req, res) => {
    res.json({ message: 'System is rebooting in 3 seconds...' });
    console.log('Reboot command received. Rebooting soon...');
    
    setTimeout(() => {
        exec(`${HOST_NSENTER} reboot`, (error, stdout, stderr) => {
            if (error) console.error(`Reboot error: ${error}`);
        });
    }, 3000);
});

// 重启 AI Engine 宿主机服务
app.post('/api/system/restart-ai', (req, res) => {
    console.log('Restarting AI Engine host service...');
    exec(`${HOST_NSENTER} systemctl restart ai-engine`, (error, stdout, stderr) => {
        if (error) {
            console.error(`AI Engine restart failed: ${error}`);
            return res.status(500).json({ error: 'Failed to restart AI Engine' });
        }
        res.json({ message: 'AI Engine restarted successfully' });
    });
});

// 重启后端服务 (容器自身重启)
app.post('/api/system/restart-backend', (req, res) => {
    res.json({ message: 'Backend is restarting...' });
    console.log('Backend restart requested. Exiting process...');
    setTimeout(() => {
        process.exit(0); // 依赖 Docker restart: always
    }, 1000);
});

// 重新部署前端 (触发 Docker 容器拉取最新静态文件)
app.post('/api/system/redeploy-frontend', (req, res) => {
    console.log('Redeploying frontend...');
    // 这里通过 nsenter 执行宿主机的 docker compose 命令
    const cmd = `cd ${PROJECT_DIR} && ${HOST_NSENTER} docker compose up -d --build web-manager-frontend-deploy && ${HOST_NSENTER} docker compose restart web-nginx`;
    exec(cmd, (error, stdout, stderr) => {
        if (error) {
            console.error(`Frontend redeploy failed: ${error}`);
            return res.status(500).json({ error: 'Failed to redeploy frontend' });
        }
        res.json({ message: 'Frontend redeployed successfully' });
    });
});

// --- 2. OTA 升级 API ---
app.post('/api/system/update', (req, res) => {
    res.json({ message: 'Update started. System will pull latest code and restart host ai-engine service.' });

    const updateCommand = `
        cd ${PROJECT_DIR} && \
        git reset --hard HEAD && \
        git pull origin main && \
        ${HOST_NSENTER} systemctl daemon-reload && \
        ${HOST_NSENTER} systemctl restart ai-engine && \
        ${HOST_NSENTER} systemctl status ai-engine --no-pager -n 50
    `;

    console.log('Executing OTA update (Git Pull + Host systemd restart)...');
    exec(updateCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`OTA Update failed: ${error}`);
            if (stderr) console.error(stderr);
        } else {
            console.log(`OTA Update success: ${stdout}`);
        }
    });
});

// --- 3. 业务配置 (AI Engine Config) API ---
app.get('/api/ai/status', (req, res) => {
    try {
        const config = fs.existsSync(CONFIG_PATH) ? JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')) : { streams: { smoking: [], occupancy: [] } };
        
        exec(`${HOST_NSENTER} systemctl is-active ai-engine`, (err, stdout) => {
            const isAiEngineUp = (stdout || '').trim() === 'active';
            
            let tasks = [];
            if (config.streams) {
                if (config.streams.smoking) {
                    config.streams.smoking.forEach(s => {
                        tasks.push({
                            camId: s.id,
                            taskType: 'smoking',
                            status: isAiEngineUp ? 'Running' : 'Offline'
                        });
                    });
                }
                if (config.streams.occupancy) {
                    config.streams.occupancy.forEach(s => {
                        tasks.push({
                            camId: s.id,
                            taskType: 'occupancy',
                            status: isAiEngineUp ? 'Running' : 'Offline'
                        });
                    });
                }
            }
            res.json(tasks);
        });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});
app.get('/api/config', (req, res) => {
    try {
        if (!fs.existsSync(CONFIG_PATH)) {
            return res.status(404).json({ error: 'Config file not found' });
        }
        const data = fs.readFileSync(CONFIG_PATH, 'utf8');
        res.json(JSON.parse(data));
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.post('/api/config', (req, res) => {
    try {
        const oldConfig = fs.existsSync(CONFIG_PATH) ? JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8')) : { streams: { smoking: [], occupancy: [] } };
        const newConfig = req.body;
        
        // Save new config
        fs.writeFileSync(CONFIG_PATH, JSON.stringify(newConfig, null, 4), 'utf8');
        
        // Restart AI Engine host service
        exec(`${HOST_NSENTER} systemctl restart ai-engine`, (err) => {
             if (err) console.error("Failed to restart ai-engine host service:", err);
        });
        res.json({ message: 'Config saved successfully and ai-engine service restarted.' });
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// --- 4. 网络配置 API ---
app.get('/api/network', (req, res) => {
    // 获取当前默认网卡的网络信息
    const cmd = `${HOST_NSENTER} nmcli -t -f IP4.ADDRESS,IP4.GATEWAY,IP4.DNS,IP4.DOMAIN device show eth0 || ${HOST_NSENTER} nmcli -t -f IP4.ADDRESS,IP4.GATEWAY,IP4.DNS,IP4.DOMAIN device show wlan0`;
    
    exec(cmd, (err, stdout) => {
        if (err) {
            return res.json({ mode: 'dhcp', ip: '', netmask: '', gateway: '', dns: '' });
        }
        
        const info = {};
        stdout.split('\n').forEach(line => {
            const [key, value] = line.split(':');
            if (key === 'IP4.ADDRESS[1]') info.ip = value.split('/')[0];
            if (key === 'IP4.GATEWAY') info.gateway = value;
            if (key === 'IP4.DNS[1]') info.dns = value;
        });

        // 简单判断模式
        exec(`${HOST_NSENTER} nmcli device show eth0 | grep "ipv4.method"`, (mErr, mStdout) => {
            const mode = (mStdout || '').includes('manual') ? 'static' : 'dhcp';
            res.json({
                mode: mode,
                ip: info.ip || '',
                netmask: '255.255.255.0', // 简化处理
                gateway: info.gateway || '',
                dns: info.dns || ''
            });
        });
    });
});

app.post('/api/network', (req, res) => {
    const { mode, ip, gateway, dns } = req.body;
    console.log('Applying new network settings:', req.body);
    
    let cmd = '';
    if (mode === 'dhcp') {
        cmd = `${HOST_NSENTER} nmcli con mod eth0 ipv4.method auto && ${HOST_NSENTER} nmcli con up eth0`;
    } else {
        cmd = `${HOST_NSENTER} nmcli con mod eth0 ipv4.addresses ${ip}/24 ipv4.gateway ${gateway} ipv4.dns "${dns}" ipv4.method manual && ${HOST_NSENTER} nmcli con up eth0`;
    }

    exec(cmd, (error, stdout, stderr) => {
        if (error) {
            console.error(`Network apply failed: ${error}`);
            return res.status(500).json({ error: 'Failed to apply network settings' });
        }
        res.json({ message: 'Network settings applied. System may disconnect.' });
    });
});

// --- 5. Occupancy Logs API ---
app.get('/api/occupancy/summary/:date', (req, res) => {
    const { date } = req.params;
    const summaryPath = path.join('/app/www/occupancy_logs', date, 'daily_summary.json');
    
    try {
        if (fs.existsSync(summaryPath)) {
            const data = fs.readFileSync(summaryPath, 'utf8');
            res.json(JSON.parse(data));
        } else {
            res.status(404).json({ error: 'Summary not found' });
        }
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/occupancy/areas', (req, res) => {
    const logsDir = '/app/www/occupancy_logs';
    try {
        if (!fs.existsSync(logsDir)) return res.json([]);
        
        let areaSet = new Set();
        const dates = fs.readdirSync(logsDir).filter(f => fs.statSync(path.join(logsDir, f)).isDirectory());
        
        // 只扫描最近 7 天的文件夹来获取场景列表，提高速度
        dates.sort().reverse().slice(0, 7).forEach(date => {
            const dateDir = path.join(logsDir, date);
            const areas = fs.readdirSync(dateDir).filter(f => fs.statSync(path.join(dateDir, f)).isDirectory());
            areas.forEach(a => areaSet.add(a.replace(/_/g, '/'))); // 恢复斜杠显示
        });
        
        res.json(Array.from(areaSet));
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

app.get('/api/occupancy/logs', (req, res) => {
    const logsDir = '/app/www/occupancy_logs';
    const { areaCode, days } = req.query;
    const maxDays = parseInt(days) || 4;

    try {
        if (!fs.existsSync(logsDir)) {
            return res.json([]);
        }

        let results = [];
        let dates = fs.readdirSync(logsDir).filter(f => fs.statSync(path.join(logsDir, f)).isDirectory());
        
        // 按日期降序排列并截取
        dates.sort().reverse();
        const targetDates = dates.slice(0, maxDays);
        
        targetDates.forEach(date => {
            const dateDir = path.join(logsDir, date);
            let areas = fs.readdirSync(dateDir).filter(f => fs.statSync(path.join(dateDir, f)).isDirectory());
            
            // 如果提供了 areaCode，只处理该场景。注意：前端传来的 areaCode 可能是斜杠，文件夹是下划线
            if (areaCode) {
                const safeArea = areaCode.replace(/\//g, '_').replace(/\\/g, '_');
                areas = areas.filter(a => a === safeArea);
            }

            areas.forEach(area => {
                const areaDir = path.join(dateDir, area);
                const files = fs.readdirSync(areaDir);
                
                // 只看 JSON 文件
                const jsonFiles = files.filter(f => f.endsWith('.json'));
                jsonFiles.forEach(jf => {
                    try {
                        const content = fs.readFileSync(path.join(areaDir, jf), 'utf8');
                        const data = JSON.parse(content);
                        data.date = date;
                        data.id = `${date}_${area}_${jf}`;
                        results.push(data);
                    } catch (e) {
                        console.error(`Error reading json log ${jf}:`, e);
                    }
                });
            });
        });
        
        results.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        res.json(results);
    } catch (e) {
        console.error("Occupancy Logs API Error:", e);
        res.status(500).json({ error: e.message });
    }
});

// --- 6. Gemma Local Model API ---
const GEMMA_HOST = process.env.GEMMA_HOST || 'host.docker.internal'; // 优先连接宿主机直跑的 Gemma
const GEMMA_PORT = process.env.GEMMA_PORT || 8080;
const AI_ENGINE_HOST = process.env.AI_ENGINE_HOST || 'host.docker.internal'; // AI Engine 在宿主机直跑
const AI_ENGINE_PORT = process.env.AI_ENGINE_PORT || 5000;

app.post('/api/ai/test', (req, res) => {
    const { image, conf_thres } = req.body;
    
    console.log(`[AI Test] Forwarding request to ${AI_ENGINE_HOST}:${AI_ENGINE_PORT}/predict...`);
    
    const payload = JSON.stringify({ image, conf_thres });
    const options = {
        hostname: AI_ENGINE_HOST,
        port: AI_ENGINE_PORT,
        path: '/predict',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    const aiReq = http.request(options, (aiRes) => {
        let data = '';
        aiRes.on('data', (chunk) => { data += chunk; });
        aiRes.on('end', () => {
            try {
                res.json(JSON.parse(data));
            } catch (e) {
                res.status(500).json({ error: 'Failed to parse AI Engine response', raw: data });
            }
        });
    });

    aiReq.on('error', (err) => {
        res.status(500).json({ error: 'Failed to connect to AI Engine', details: err.message });
    });

    aiReq.write(payload);
    aiReq.end();
});

app.get('/api/gemma/status', (req, res) => {
    let statusData = { status: 'Offline', details: null };

    // Helper to make GET requests to Gemma
    const fetchGemma = (path) => {
        return new Promise((resolve) => {
            http.get(`http://${GEMMA_HOST}:${GEMMA_PORT}${path}`, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve({ statusCode: res.statusCode, data: JSON.parse(data) });
                    } catch (e) {
                        resolve({ statusCode: res.statusCode, data: null });
                    }
                });
            }).on('error', () => resolve({ statusCode: 500, data: null }));
        });
    };

    // First check health
    fetchGemma('/health').then(async (healthRes) => {
        if (healthRes.statusCode === 200 && healthRes.data?.status === 'ok') {
            statusData.status = 'Running';
            
            // Fetch slots for real-time processing status
            const slotsRes = await fetchGemma('/slots');
            const propsRes = await fetchGemma('/props');
            
            statusData.details = {
                health: healthRes.data,
                slots: slotsRes.data || [],
                props: propsRes.data || {}
            };
        } else if (healthRes.data?.status === 'loading model') {
            statusData.status = 'Loading';
            statusData.details = { health: healthRes.data };
        } else if (healthRes.statusCode !== 500) {
            statusData.status = 'Error';
        }
        res.json(statusData);
    });
});

const clearGemmaCache = () => {
    // 兼容新版 llama-server API: POST /slots/{id}?action=release
    const postOptions = {
        hostname: GEMMA_HOST,
        port: GEMMA_PORT,
        path: '/slots/0?action=release',
        method: 'POST'
    };
    const postReq = http.request(postOptions, (res) => {
        if (res.statusCode !== 200) {
            // 如果 POST 也失败，尝试旧版 DELETE (以防万一)
            const deleteOptions = { ...postOptions, path: '/slots/0', method: 'DELETE' };
            http.request(deleteOptions).end();
        }
    });
    postReq.on('error', () => {});
    postReq.end();
};

app.post('/api/gemma/infer', (req, res) => {
    const { image, prompt, enableThinking } = req.body; 

    // 强制 JSON 输出的 System Prompt
    const systemPrompt = (
        "You are a professional image analyzer. You MUST output a JSON object ONLY. " +
        "Structure: {\"result\": \"YES/NO/SUCCESS\", \"analysis\": \"your detailed observation or result\"}"
    );

    const payload = JSON.stringify({
        model: "buildingos_review_engine",
        messages: [
            {
                role: "system",
                content: systemPrompt
            },
            {
                role: "user",
                content: [
                    { type: "image_url", image_url: { url: image } },
                    { type: "text", text: prompt || "检测图片中是否有活人存在，仔细鉴别头肩和肢体等人体要输，如果有人回答YES，并且告知在什么位置。没有则回答NO" }
                ]
            }
        ],
        chat_template_kwargs: {
            enable_thinking: enableThinking !== undefined ? enableThinking : false 
        },
        stream: false,
        temperature: 0.0,
        max_tokens: 512
    });

    const options = {
        hostname: GEMMA_HOST,
        port: GEMMA_PORT,
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(payload)
        }
    };

    const startTime = Date.now();

    const gemmaReq = http.request(options, (gemmaRes) => {
        let data = '';
        gemmaRes.on('data', (chunk) => { data += chunk; });
        gemmaRes.on('end', () => {
            const duration = Date.now() - startTime;
            try {
                const response = JSON.parse(data);
                const content = response.choices?.[0]?.message?.content || '';
                
                let result = 'UNKNOWN';
                let reasoning = response.choices?.[0]?.message?.reasoning_content || '';
                
                try {
                    // 清理 Markdown 代码块
                    const cleanContent = content.replace(/```json/g, "").replace(/```/g, "").trim();
                    const parsed = JSON.parse(cleanContent);
                    result = parsed.result || 'UNKNOWN';
                    if (parsed.analysis) reasoning = parsed.analysis;
                } catch (e) {
                    console.warn("Manual infer JSON parse failed, fallback to text search");
                    if (content.toUpperCase().includes("YES")) result = "YES";
                    else if (content.toUpperCase().includes("NO")) result = "NO";
                    else result = content.substring(0, 50); // Fallback for descriptions
                }

                res.json({ 
                    result: result, 
                    prompt: prompt,
                    llm_response: content,
                    reasoning: reasoning,
                    usage: response.usage,
                    durationMs: duration
                });
            } catch (e) {
                res.status(500).json({ error: 'Failed to parse Gemma response', raw: data });
            } finally {
                clearGemmaCache();
            }
        });
    });

    gemmaReq.on('error', (err) => {
        res.status(500).json({ error: 'Failed to connect to Gemma server', details: err.message });
        clearGemmaCache();
    });

    gemmaReq.write(payload);
    gemmaReq.end();
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Backend server running on http://localhost:${PORT}`);
});

<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- System Info Card -->
      <el-col :span="12">
        <el-card class="box-card system-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Monitor /></el-icon> {{ $t('dashboard.nodeStatus') }} ({{ sysInfo.board.model }})</span>
            </div>
          </template>
          <div v-loading="loadingSys" class="sys-content">
            <!-- First Row: Main Usage Metrics -->
            <el-row :gutter="10" class="sys-metrics">
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="sysInfo.cpu.usage" :color="customColors" :width="100">
                  <template #default="{ percentage }">
                    <span class="percentage-value">{{ percentage.toFixed(0) }}%</span>
                    <span class="percentage-label">{{ $t('dashboard.cpuLoad') }}</span>
                  </template>
                </el-progress>
                <div class="metric-desc">{{ sysInfo.cpu.cores }} Cores</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="sysInfo.memory.ram.usagePercent" :color="customColors" :width="100">
                  <template #default="{ percentage }">
                    <span class="percentage-value">{{ percentage.toFixed(0) }}%</span>
                    <span class="percentage-label">{{ $t('dashboard.unifiedMem') }}</span>
                  </template>
                </el-progress>
                <div class="metric-desc">{{ formatBytes(sysInfo.memory.ram.used) }} / {{ formatBytes(sysInfo.memory.ram.total) }}</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="sysInfo.memory.swap.usagePercent" :color="customColors" :width="100">
                  <template #default="{ percentage }">
                    <span class="percentage-value">{{ percentage.toFixed(0) }}%</span>
                    <span class="percentage-label">{{ $t('dashboard.swap') }}</span>
                  </template>
                </el-progress>
                <div class="metric-desc">{{ formatBytes(sysInfo.memory.swap.used) }} / {{ formatBytes(sysInfo.memory.swap.total) }}</div>
              </el-col>
              <el-col :span="6" class="metric-item">
                <el-progress type="dashboard" :percentage="sysInfo.disk?.percent || 0" :color="customColors" :width="100">
                  <template #default="{ percentage }">
                    <span class="percentage-value">{{ percentage.toFixed(0) }}%</span>
                    <span class="percentage-label">{{ $t('dashboard.diskUsage') }}</span>
                  </template>
                </el-progress>
                <div class="metric-desc" v-if="sysInfo.disk?.total > 0">
                  {{ formatBytes(sysInfo.disk.used) }} / {{ formatBytes(sysInfo.disk.total) }}
                </div>
                <div class="metric-desc" v-else>Loading...</div>
              </el-col>
            </el-row>
            
            <el-divider style="margin: 10px 0;" />
            
            <!-- Second Row: Hardware Vitals (Power, Temp) -->
            <el-descriptions :column="2" border size="small">
              <el-descriptions-item :label="$t('dashboard.power')">
                <el-tag size="small" type="warning" effect="plain">{{ (sysInfo.power.total / 1000).toFixed(1) }} W</el-tag>
                <span style="font-size: 12px; color: #909399; margin-left: 5px;">(CPU+GPU+CV: {{ (powerComputeRail / 1000).toFixed(1) }} W)</span>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('dashboard.temp')">
                <span style="font-size: 12px;">
                  GPU: <span :style="{ color: gpuTemp > 75 ? 'red' : 'inherit' }">{{ gpuTemp || 'N/A' }}°C</span> | 
                  CPU: <span :style="{ color: cpuTemp > 75 ? 'red' : 'inherit' }">{{ cpuTemp || 'N/A' }}°C</span>
                </span>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('dashboard.nvpModel')">
                <el-tag size="small" type="success">{{ sysInfo.board.nvpmodel }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="$t('dashboard.uptime')">{{ formatUptime(sysInfo.board.uptime) }}</el-descriptions-item>
            </el-descriptions>

            <el-divider style="margin: 10px 0;" />

            <el-alert
              v-for="(warning, idx) in systemWarnings"
              :key="idx"
              :title="warning"
              type="warning"
              show-icon
              :closable="false"
              class="warning-item"
            />

            <el-card shadow="never" class="engine-panel">
              <div class="engine-header">{{ $t('dashboard.enginePanel') }}</div>
              <div class="engine-tags">
                <el-tag
                  v-for="engine in engineEntries"
                  :key="engine.name"
                  size="small"
                  :type="engine.value > 60 ? 'danger' : (engine.value > 0 ? 'warning' : 'info')"
                >
                  {{ engine.name }}: {{ formatEngineValue(engine.value) }}
                </el-tag>
              </div>
              <div class="engine-note">{{ $t('dashboard.engineNote') }}</div>
              <div v-if="isEngineAllIdle" class="engine-idle-note">{{ $t('dashboard.engineIdleNote') }}</div>
            </el-card>
          </div>
        </el-card>

        <!-- Gemma Local Model Status Card -->
        <el-card class="box-card gemma-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Cpu /></el-icon> {{ $t('dashboard.gemmaStatus') }} (Gemma 4 E2B)</span>
              <el-tag size="small" :type="gemmaStatus === 'Running' ? 'success' : (gemmaStatus === 'Loading' ? 'warning' : 'danger')">
                <span style="display: flex; align-items: center; gap: 5px;">
                  <span v-if="gemmaStatus === 'Running'" class="status-dot green"></span>
                  <span v-else-if="gemmaStatus === 'Loading'" class="status-dot yellow"></span>
                  <span v-else class="status-dot red"></span>
                  {{ gemmaStatus }}
                </span>
              </el-tag>
            </div>
          </template>
          <div class="gemma-content" v-loading="loadingSys">
            <el-descriptions :column="1" border size="small" v-if="gemmaStatus === 'Running' && gemmaDetails">
              <el-descriptions-item :label="$t('dashboard.modelInstance')">
                {{ gemmaDetails.props?.default_generation_settings?.model || 'llama.cpp GGUF Model' }}
              </el-descriptions-item>
              <el-descriptions-item label="上下文容量 (Context Size)">
                {{ gemmaDetails.props?.default_generation_settings?.n_ctx || 'Unknown' }} Tokens
              </el-descriptions-item>
              <el-descriptions-item :label="$t('dashboard.runStatus')">
                <div v-if="gemmaDetails.slots && gemmaDetails.slots.length > 0">
                  <div v-for="slot in gemmaDetails.slots" :key="slot.id" style="margin-bottom: 5px;">
                    <el-tag size="small" :type="slot.state === 0 ? 'info' : 'primary'">
                      Slot {{ slot.id }}: {{ slot.state === 0 ? 'Idle (空闲)' : 'Running (运行中)' }}
                    </el-tag>
                    <span v-if="slot.state !== 0" style="margin-left: 10px; font-size: 12px; color: #606266;">
                      Prompt: {{ slot.n_prompt_tokens }} | Decoded: {{ slot.n_decoded_tokens }}
                    </span>
                  </div>
                </div>
                <div v-else>
                  <el-tag size="small" type="info">Idle (空闲)</el-tag>
                </div>
              </el-descriptions-item>
            </el-descriptions>
            <div v-else-if="gemmaStatus === 'Loading'">
              <el-alert :title="$t('dashboard.modelLoading')" type="warning" show-icon :closable="false" />
            </div>
            <div v-else>
              <el-alert :title="$t('dashboard.modelOffline')" type="error" show-icon :closable="false" />
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- ZLM Media Server Status Card -->
      <el-col :span="12">
        <el-card class="box-card zlm-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><VideoCamera /></el-icon> {{ $t('dashboard.zlmStatus') }} (ZLMediaKit)</span>
              <el-tag size="small" type="info">{{ $t('dashboard.refreshPerSec') }}</el-tag>
            </div>
          </template>
          <div class="zlm-content">
            <el-row :gutter="20" style="margin-bottom: 20px;">
              <el-col :span="8">
                <el-statistic :title="$t('dashboard.activeStreams')" :value="uniqueStreams.length" />
              </el-col>
              <el-col :span="8">
                <el-statistic :title="$t('dashboard.totalProtocols')" :value="zlmData.length" />
              </el-col>
              <el-col :span="8">
                <el-statistic :title="$t('dashboard.totalBandwidth')" :value="formatBytes(totalBandwidth) + '/s'" />
              </el-col>
            </el-row>

            <el-table :data="uniqueStreamsData" height="150" style="width: 100%" size="small" border>
              <el-table-column prop="stream" :label="$t('dashboard.streamId')" width="120" />
              <el-table-column :label="$t('dashboard.schemas')">
                <template #default="scope">
                  <el-tag 
                    v-for="schema in scope.row.schemas" 
                    :key="schema" 
                    size="small" 
                    style="margin-right: 5px; margin-bottom: 5px;"
                    :type="schema === 'rtsp' ? 'success' : (schema === 'rtmp' ? 'warning' : 'info')"
                  >
                    {{ schema.toUpperCase() }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="$t('dashboard.uptime')" width="100">
                <template #default="scope">
                  {{ formatUptime(scope.row.aliveSecond) }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- AI Engine Status Card -->
        <el-card class="box-card ai-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Cpu /></el-icon> {{ $t('dashboard.aiTasks') }}</span>
            </div>
          </template>
          <div class="ai-content">
             <el-table :data="aiTasks" height="150" style="width: 100%" size="small" border>
              <el-table-column prop="camId" :label="$t('dashboard.cameraId')" width="100" />
              <el-table-column prop="taskType" :label="$t('dashboard.algoType')" width="120">
                 <template #default="scope">
                    <el-tag size="small" :type="scope.row.taskType === 'smoking' ? 'danger' : 'primary'">
                      {{ scope.row.taskType === 'smoking' ? $t('dashboard.smoking') : $t('dashboard.presence') }}
                    </el-tag>
                 </template>
              </el-table-column>
              <el-table-column prop="status" :label="$t('dashboard.status')">
                 <template #default="scope">
                    <el-tag size="small" :type="scope.row.status === 'Running' ? 'success' : 'warning'">
                      <span style="display: flex; align-items: center; gap: 5px;">
                        <span v-if="scope.row.status === 'Running'" class="status-dot green"></span>
                        <span v-else class="status-dot yellow"></span>
                        {{ scope.row.status }}
                      </span>
                    </el-tag>
                 </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>

        <!-- System Management Card -->
        <el-card class="box-card manage-card">
          <template #header>
            <div class="card-header">
              <span><el-icon><Setting /></el-icon> {{ $t('dashboard.sysManage') }}</span>
            </div>
          </template>
          <div class="manage-content">
            <el-row :gutter="10">
              <el-col :span="8">
                <el-button type="primary" plain style="width: 100%" @click="handleRestartAi">
                  <el-icon><Refresh /></el-icon> {{ $t('dashboard.restartAi') }}
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button type="warning" plain style="width: 100%" @click="handleRestartBackend">
                  <el-icon><Connection /></el-icon> {{ $t('dashboard.restartBackend') }}
                </el-button>
              </el-col>
              <el-col :span="8">
                <el-button type="danger" plain style="width: 100%" @click="handleRedeployFrontend">
                  <el-icon><Upload /></el-icon> {{ $t('dashboard.redeployFrontend') }}
                </el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { Monitor, VideoCamera, Cpu, Setting, Refresh, Connection, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const router = useRouter()
const loadingSys = ref(false)
let refreshInterval = null
let zlmInterval = null
const prevSwapUsed = ref(0)
const prevGpuFreq = ref(0)
const systemWarnings = ref([])

// Sys Info State
const sysInfo = ref({
  cpu: { usage: 0, cores: 0, details: {} },
  memory: { 
    ram: { usagePercent: 0, used: 0, total: 0 },
    swap: { usagePercent: 0, used: 0, total: 0 }
  },
  gpu: { util: 0, memUsed: 0, memTotal: 0, freq: 0 },
  disk: { used: 0, total: 0, percent: 0 },
  engines: {},
  power: { total: 0, gpu: 0, cpu: 0 },
  temperature: {},
  board: { model: 'Loading...', jetpack: '', nvpmodel: '', uptime: 0 }
})

// ZLM State
const zlmData = ref([])

// AI Tasks State
const aiTasks = ref([])

// Gemma State
const gemmaStatus = ref('Unknown')
const gemmaDetails = ref(null)

const customColors = [
  { color: '#5cb87a', percentage: 60 },
  { color: '#e6a23c', percentage: 80 },
  { color: '#f56c6c', percentage: 100 },
]

// Computed properties for ZLM
const uniqueStreams = computed(() => {
  return [...new Set(zlmData.value.map(item => item.stream))]
})

const uniqueStreamsData = computed(() => {
  const map = {}
  zlmData.value.forEach(item => {
    if (!map[item.stream]) {
      map[item.stream] = {
        stream: item.stream,
        schemas: [],
        aliveSecond: item.aliveSecond
      }
    }
    map[item.stream].schemas.push(item.schema)
  })
  return Object.values(map)
})

const totalBandwidth = computed(() => {
  // Only sum up the pull origin streams to avoid double counting
  const pulls = zlmData.value.filter(item => item.originTypeStr === 'pull' && item.schema === 'rtsp')
  if (pulls.length > 0) {
      return pulls.reduce((sum, item) => sum + (item.bytesSpeed || 0), 0)
  }
  return zlmData.value.reduce((sum, item) => sum + (item.bytesSpeed || 0), 0) / zlmData.value.length || 0; 
})

const engineEntries = computed(() => {
  const engines = sysInfo.value.engines || {}
  return Object.entries(engines).map(([name, value]) => ({
    name,
    value: typeof value === 'number' ? value : (value ? 100 : 0)
  }))
})

const isEngineAllIdle = computed(() => {
  if (engineEntries.value.length === 0) return true
  return engineEntries.value.every(item => (item.value || 0) <= 0)
})

const powerComputeRail = computed(() => {
  const power = sysInfo.value.power || {}
  const rail = power.cpu_gpu_cv || 0
  return rail > 0 ? rail : (power.gpu || 0)
})

const getTempByKeys = (keys) => {
  const temps = sysInfo.value.temperature || {}
  const found = Object.entries(temps).find(([name]) => keys.includes(name))
  return found ? found[1] : 0
}

const gpuTemp = computed(() => getTempByKeys(['GPU', 'gpu', 'GPU-therm', 'gpu-therm', 'TGPU']))
const cpuTemp = computed(() => getTempByKeys(['CPU', 'cpu', 'CPU-therm', 'cpu-therm', 'TCPU']))

// Formatting Helpers
const formatBytes = (bytes, decimals = 2) => {
  if (!+bytes) return '0 Bytes'
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
}

const formatUptime = (seconds) => {
  if (!seconds) return '0s'
  const d = Math.floor(seconds / (3600*24))
  const h = Math.floor(seconds % (3600*24) / 3600)
  const m = Math.floor(seconds % 3600 / 60)
  const s = Math.floor(seconds % 60)
  
  const dDisplay = d > 0 ? d + "d " : ""
  const hDisplay = h > 0 ? h + "h " : ""
  const mDisplay = m > 0 ? m + "m " : ""
  const sDisplay = s > 0 ? s + "s" : ""
  return dDisplay + hDisplay + mDisplay + sDisplay
}

const formatEngineValue = (value) => {
  if (typeof value !== 'number') return String(value)
  return `${value.toFixed(0)}%`
}

const updateWarnings = (data) => {
  const warnings = []
  const ramUsage = data?.memory?.ram?.usagePercent || 0
  const swapUsage = data?.memory?.swap?.usagePercent || 0
  const swapUsed = data?.memory?.swap?.used || 0
  const gpuUtil = data?.gpu?.util || 0
  const gpuFreq = data?.gpu?.freq || 0

  if (ramUsage >= 90) {
    warnings.push(t('dashboard.warnRam'))
  }

  if (swapUsage >= 50) {
    warnings.push(t('dashboard.warnSwap'))
  }

  if (prevSwapUsed.value > 0) {
    const swapDeltaMb = (swapUsed - prevSwapUsed.value) / (1024 * 1024)
    if (swapDeltaMb > 20) {
      warnings.push(t('dashboard.warnSwapDelta', { delta: swapDeltaMb.toFixed(1) }))
    }
  }

  if (prevGpuFreq.value > 0 && gpuUtil >= 85 && gpuFreq < prevGpuFreq.value * 0.85) {
    warnings.push(t('dashboard.warnGpuFreq'))
  }

  if (gpuTemp.value >= 80 || cpuTemp.value >= 80) {
    warnings.push(t('dashboard.warnTemp'))
  }

  const engines = data?.engines || {}
  const heavyEngines = Object.entries(engines)
    .filter(([, value]) => typeof value === 'number' && value >= 60)
    .map(([name]) => name)
  if (heavyEngines.length > 0) {
    warnings.push(t('dashboard.warnEngines', { engines: heavyEngines.join('、') }))
  }

  systemWarnings.value = warnings
  prevSwapUsed.value = swapUsed
  prevGpuFreq.value = gpuFreq
}

// Fetchers
const fetchSysInfo = async () => {
  try {
    const res = await axios.get('/api/system/info')
    sysInfo.value = res.data
    updateWarnings(res.data)
  } catch (e) {
    systemWarnings.value = [t('dashboard.fetchFailed')]
  }
}

const fetchZlmMetrics = async () => {
  try {
    const res = await axios.get('/api/zlm/metrics')
    if (res.data.code === 0 && res.data.data) {
      zlmData.value = res.data.data
    } else {
      zlmData.value = []
    }
  } catch (e) {
    // console.error('Failed to fetch ZLM metrics')
  }
}

const fetchAiTasks = async () => {
  try {
    const res = await axios.get('/api/ai/status')
    aiTasks.value = res.data
  } catch (e) {
    // console.error('Failed to fetch AI status')
  }
}

const fetchGemmaStatus = async () => {
  try {
    const res = await axios.get('/api/gemma/status')
    gemmaStatus.value = res.data.status
    gemmaDetails.value = res.data.details
  } catch (e) {
    gemmaStatus.value = 'Offline'
    gemmaDetails.value = null
  }
}

// Management Handlers
const handleRestartAi = async () => {
  try {
    await ElMessageBox.confirm(
      t('dashboard.restartAiConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    )
    const res = await axios.post('/api/system/restart-ai')
    ElMessage.success(res.data.message)
    setTimeout(() => fetchAiTasks(), 2000)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(t('params.saveFailed'))
  }
}

const handleRestartBackend = async () => {
  try {
    await ElMessageBox.confirm(
      t('dashboard.restartBackendConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    )
    await axios.post('/api/system/restart-backend')
    ElMessage.success(t('common.rebooting'))
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(t('params.saveFailed'))
  }
}

const handleRedeployFrontend = async () => {
  try {
    await ElMessageBox.confirm(
      t('dashboard.redeployFrontendConfirm'),
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning',
      }
    )
    const res = await axios.post('/api/system/redeploy-frontend')
    ElMessage.success(res.data.message)
    setTimeout(() => {
      window.location.reload()
    }, 3000)
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(t('params.saveFailed'))
  }
}

onMounted(() => {
  loadingSys.value = true
  Promise.all([fetchSysInfo(), fetchZlmMetrics(), fetchAiTasks(), fetchGemmaStatus()]).finally(() => {
    loadingSys.value = false
  })
  
  refreshInterval = setInterval(() => {
    fetchSysInfo()
    fetchAiTasks()
  }, 1000)

  // Refresh ZLM metrics every 1 second
  zlmInterval = setInterval(() => {
    fetchZlmMetrics()
    fetchGemmaStatus() // fetch Gemma real-time slot state often
  }, 1000)
})

onBeforeUnmount(() => {
  if (refreshInterval) clearInterval(refreshInterval)
  if (zlmInterval) clearInterval(zlmInterval)
})
</script>

<style scoped>
.dashboard-container {
  padding: 10px;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.sys-metrics {
  text-align: center;
  margin-bottom: 20px;
}
.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.percentage-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}
.percentage-label {
  display: block;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
.metric-desc {
  margin-top: 10px;
  font-size: 13px;
  color: #606266;
}
.metric-note {
  margin-top: 4px;
  font-size: 11px;
  color: #909399;
  text-align: center;
}
.warning-item {
  margin-top: 8px;
}
.engine-panel {
  margin-top: 10px;
  border: 1px solid #ebeef5;
}
.engine-header {
  font-size: 13px;
  color: #303133;
  font-weight: 600;
  margin-bottom: 8px;
}
.engine-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.engine-note {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
.engine-idle-note {
  margin-top: 6px;
  font-size: 12px;
  color: #67c23a;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.status-dot.green {
  background-color: #67C23A;
  box-shadow: 0 0 5px #67C23A;
}
.status-dot.yellow {
  background-color: #E6A23C;
  box-shadow: 0 0 5px #E6A23C;
}
.status-dot.red {
  background-color: #F56C6C;
  box-shadow: 0 0 5px #F56C6C;
}
</style>

<template>
  <div class="ai-monitor-container">
    <el-row :gutter="20" style="height: 100%;">
      <!-- Left: Camera Grid -->
      <el-col :span="16" style="height: 100%;">
        <el-card class="box-card video-card" body-style="height: calc(100% - 60px); padding: 10px;">
          <template #header>
            <div class="card-header">
              <span><el-icon><VideoCamera /></el-icon> {{ $t('monitor.videoMatrix') }}</span>
              <el-tag type="success" size="small" v-if="cameras.length > 0">{{ $t('monitor.onlineCount', { count: cameras.length }) }}</el-tag>
            </div>
          </template>
          <CameraGrid v-if="cameras.length > 0" :cameras="cameras" />
          <el-empty v-else :description="$t('monitor.noConfig')" />
        </el-card>
      </el-col>

      <!-- Right: AI Logs & Events -->
      <el-col :span="8" style="height: 100%;">
        <el-card class="box-card logs-card" body-style="height: calc(100% - 60px); padding: 0; display: flex; flex-direction: column;">
          <template #header>
            <div class="card-header">
              <span><el-icon><DataLine /></el-icon> {{ $t('monitor.aiLogs') }}</span>
              <el-switch v-model="autoScroll" :active-text="$t('monitor.autoScroll')" size="small" />
            </div>
          </template>
          
          <div class="log-terminal" ref="logContainer">
            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="getLogClass(log.message)">
              <span class="log-time">[{{ formatTime(log.timestamp) }}]</span>
              <span class="log-cam" v-if="log.camId && log.camId !== 'system'">[{{ log.camId }}]</span>
              <span class="log-msg">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { VideoCamera, DataLine } from '@element-plus/icons-vue'
import { io } from 'socket.io-client'
import CameraGrid from './CameraGrid.vue'

const { t } = useI18n()
const cameras = ref([])
const logs = ref([])
const autoScroll = ref(true)
const logContainer = ref(null)
let socket = null

const fetchConfig = async () => {
  try {
    const res = await axios.get('/api/config')
    const config = res.data
    const allStreams = []
    
    // Combine smoking and occupancy streams for the grid
    if (config.streams) {
      if (config.streams.smoking) {
        config.streams.smoking.forEach(s => {
            if (!allStreams.find(ex => ex.name === s.id)) {
                allStreams.push({ name: s.id, type: 'smoking' })
            }
        })
      }
      if (config.streams.occupancy) {
        config.streams.occupancy.forEach(s => {
            if (!allStreams.find(ex => ex.name === s.id)) {
                allStreams.push({ name: s.id, type: 'occupancy' })
            }
        })
      }
    }
    cameras.value = allStreams
  } catch (e) {
    console.error('Failed to fetch camera config:', e)
  }
}

const setupWebSocket = () => {
  // Connect to the backend server
  const serverUrl = window.location.hostname === 'localhost' ? 'http://localhost:3000' : ''
  socket = io(serverUrl)

  socket.on('connect', () => {
    logs.value.push({ timestamp: new Date(), message: t('monitor.logConnected'), camId: 'system' })
  })

  socket.on('log', (data) => {
    logs.value.push(data)
    // Keep only the last 1000 logs to prevent memory leaks
    if (logs.value.length > 1000) {
      logs.value.shift()
    }
  })

  socket.on('disconnect', () => {
    logs.value.push({ timestamp: new Date(), message: t('monitor.logDisconnected'), camId: 'system' })
  })
}

const formatTime = (isoString) => {
  const date = new Date(isoString)
  return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}`
}

const getLogClass = (message) => {
  if (!message) return ''
  if (message.includes('[ERROR]') || message.includes('Failed')) return 'log-error'
  if (message.includes('Warning') || message.includes('POTENTIAL')) return 'log-warning'
  if (message.includes('Triggered') || message.includes('DETECTED') || message.includes('ACTIVE')) return 'log-highlight'
  return 'log-info'
}

watch(logs, () => {
  if (autoScroll.value && logContainer.value) {
    nextTick(() => {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    })
  }
}, { deep: true })

onMounted(() => {
  fetchConfig()
  setupWebSocket()
})

onBeforeUnmount(() => {
  if (socket) {
    socket.disconnect()
  }
})
</script>

<style scoped>
.ai-monitor-container {
  padding: 10px;
  height: calc(100vh - 100px); /* Adjust based on your layout header/footer */
}

.box-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.log-terminal {
  flex: 1;
  background-color: #1e1e1e;
  color: #d4d4d4;
  padding: 10px;
  overflow-y: auto;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.log-entry {
  word-break: break-all;
  border-bottom: 1px solid #333;
  padding: 2px 0;
}

.log-time {
  color: #569cd6;
  margin-right: 5px;
}

.log-cam {
  color: #4ec9b0;
  margin-right: 5px;
  font-weight: bold;
}

.log-error {
  color: #f14c4c;
}

.log-warning {
  color: #cca700;
}

.log-highlight {
  color: #b5cea8;
  font-weight: bold;
  background-color: rgba(255, 255, 255, 0.1);
}

.log-info {
  color: #cccccc;
}
</style>

<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('cameras.title') }}</span>
        <el-button type="primary" @click="saveConfig">{{ $t('cameras.save') }}</el-button>
      </div>
    </template>

    <div v-loading="loading">
      <el-alert 
        :title="$t('cameras.architectureTip')" 
        type="info" 
        :description="$t('cameras.architectureDesc')"
        show-icon
        style="margin-bottom: 20px;"
      />

      <div v-for="(area, areaIndex) in areas" :key="area.areaCode" class="area-card">
        <el-card shadow="hover" style="margin-bottom: 20px;">
          <template #header>
            <div class="area-header">
              <span style="font-weight: bold; font-size: 16px;">
                <el-icon><Location /></el-icon> {{ $t('cameras.areaRegion') }}: {{ area.areaCode === 'UNKNOWN' ? $t('cameras.unassignedArea') : area.areaCode }}
              </span>
              <div>
                <el-button size="small" type="success" plain @click="openAddCameraDialog(area.areaCode)">{{ $t('cameras.addCamera') }}</el-button>
                <el-button size="small" type="danger" plain @click="removeArea(areaIndex)" v-if="area.areaCode !== 'UNKNOWN'">{{ $t('cameras.deleteArea') }}</el-button>
              </div>
            </div>
          </template>

          <el-table :data="area.cameras" style="width: 100%" border size="small">
            <el-table-column prop="id" :label="$t('cameras.deviceId')" width="150" />
            <el-table-column prop="name" :label="$t('cameras.locationName')" width="180" />
            <el-table-column prop="source_url" :label="$t('cameras.rtspUrl')" />
            <el-table-column :label="$t('cameras.enabledAlgorithms')" width="220">
              <template #default="scope">
                <el-checkbox-group v-model="scope.row.tasks">
                  <el-checkbox label="presence">{{ $t('cameras.presence') }}</el-checkbox>
                  <el-checkbox label="smoking">{{ $t('cameras.smoking') }}</el-checkbox>
                </el-checkbox-group>
              </template>
            </el-table-column>
            <el-table-column :label="$t('cameras.actions')" width="100">
              <template #default="scope">
                <el-button size="small" type="danger" @click="removeCamera(areaIndex, scope.$index)">{{ $t('cameras.remove') }}</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>

      <el-button type="primary" plain @click="dialogAreaVisible = true" style="width: 100%; border-style: dashed;">
        <el-icon><Plus /></el-icon> {{ $t('cameras.addNewArea') }}
      </el-button>
    </div>

    <!-- 添加场景弹窗 -->
    <el-dialog v-model="dialogAreaVisible" :title="$t('cameras.addAreaDialogTitle')" width="400px">
      <el-form label-width="100px">
        <el-form-item :label="$t('cameras.areaCode')">
          <el-input v-model="newAreaCode" :placeholder="$t('cameras.areaCodePlaceholder')"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogAreaVisible = false">{{ $t('cameras.cancel') }}</el-button>
        <el-button type="primary" @click="confirmAddArea">{{ $t('cameras.confirm') }}</el-button>
      </template>
    </el-dialog>

    <!-- 添加摄像头弹窗 -->
    <el-dialog v-model="dialogCamVisible" :title="$t('cameras.addCamera')" width="600px">
      <el-form :model="newCamera" label-width="120px">
        <el-form-item :label="$t('cameras.belongingArea')">
          <el-input v-model="currentAddAreaCode" disabled></el-input>
        </el-form-item>
        <el-form-item :label="$t('cameras.deviceId')">
          <el-input v-model="newCamera.id" :placeholder="$t('cameras.deviceIdPlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('cameras.locationName')">
          <el-input v-model="newCamera.name" :placeholder="$t('cameras.locationNamePlaceholder')"></el-input>
        </el-form-item>
        <el-form-item :label="$t('cameras.rtspUrl')">
          <el-input v-model="newCamera.source_url" placeholder="rtsp://admin:pwd@ip:554/..."></el-input>
        </el-form-item>
        <el-form-item :label="$t('cameras.initialAlgorithms')">
          <el-checkbox-group v-model="newCamera.tasks">
            <el-checkbox label="presence">{{ $t('cameras.presence') }}</el-checkbox>
            <el-checkbox label="smoking">{{ $t('cameras.smoking') }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogCamVisible = false">{{ $t('cameras.cancel') }}</el-button>
        <el-button type="primary" @click="confirmAddCamera">{{ $t('cameras.confirm') }}</el-button>
      </template>
    </el-dialog>

  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Location, Plus } from '@element-plus/icons-vue'

const { t } = useI18n()
const loading = ref(false)
const fullConfig = ref({})
const areas = ref([])

// Dialog states
const dialogAreaVisible = ref(false)
const newAreaCode = ref('')

const dialogCamVisible = ref(false)
const currentAddAreaCode = ref('')
const newCamera = ref({ id: '', name: '', source_url: '', tasks: ['presence'] })

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/config')
    fullConfig.value = res.data
    
    const streams = res.data.streams || { smoking: [], occupancy: [] }
    const areaMap = {}

    // 解析 Presence 摄像头
    streams.occupancy.forEach(cam => {
      const code = cam.areaCode || 'UNKNOWN'
      if (!areaMap[code]) areaMap[code] = { areaCode: code, cameras: [] }
      areaMap[code].cameras.push({
        id: cam.id,
        name: cam.name,
        source_url: cam.source_url,
        tasks: ['presence']
      })
    })

    // 解析 Smoking 摄像头并合并
    streams.smoking.forEach(cam => {
      const code = cam.areaCode || 'UNKNOWN'
      if (!areaMap[code]) areaMap[code] = { areaCode: code, cameras: [] }
      
      const existing = areaMap[code].cameras.find(c => c.id === cam.id)
      if (existing) {
        if (!existing.tasks.includes('smoking')) {
          existing.tasks.push('smoking')
        }
      } else {
        areaMap[code].cameras.push({
          id: cam.id,
          name: cam.name,
          source_url: cam.source_url,
          tasks: ['smoking']
        })
      }
    })

    areas.value = Object.values(areaMap)
  } catch (e) {
    ElMessage.error(t('cameras.fetchFailed'))
  }
  loading.value = false
}

const confirmAddArea = () => {
  if (!newAreaCode.value.trim()) {
    return ElMessage.warning(t('cameras.areaCodeEmpty'))
  }
  if (areas.value.find(a => a.areaCode === newAreaCode.value)) {
    return ElMessage.warning(t('cameras.areaExists'))
  }
  areas.value.push({ areaCode: newAreaCode.value, cameras: [] })
  dialogAreaVisible.value = false
  newAreaCode.value = ''
}

const removeArea = (index) => {
  areas.value.splice(index, 1)
}

const openAddCameraDialog = (areaCode) => {
  currentAddAreaCode.value = areaCode
  newCamera.value = { id: '', name: '', source_url: '', tasks: ['presence', 'smoking'] }
  dialogCamVisible.value = true
}

const confirmAddCamera = () => {
  if (!newCamera.value.id || !newCamera.value.source_url) {
    return ElMessage.warning(t('cameras.idUrlRequired'))
  }
  if (newCamera.value.tasks.length === 0) {
    return ElMessage.warning(t('cameras.taskRequired'))
  }
  
  const targetArea = areas.value.find(a => a.areaCode === currentAddAreaCode.value)
  if (targetArea) {
    // 检查 ID 是否全局冲突
    let isConflict = false
    areas.value.forEach(a => {
      if (a.cameras.find(c => c.id === newCamera.value.id)) isConflict = true
    })
    if (isConflict) return ElMessage.warning(t('cameras.idConflict'))

    targetArea.cameras.push({ ...newCamera.value })
  }
  dialogCamVisible.value = false
}

const removeCamera = (areaIndex, camIndex) => {
  areas.value[areaIndex].cameras.splice(camIndex, 1)
}

const saveConfig = async () => {
  loading.value = true
  try {
    const newStreams = { smoking: [], occupancy: [] }
    
    // 拍平回底层的 streams 结构
    areas.value.forEach(area => {
      area.cameras.forEach(cam => {
        if (cam.tasks.length === 0) return

        const streamData = {
          id: cam.id,
          name: cam.name,
          areaCode: area.areaCode,
          source_url: cam.source_url,
          zlm_stream_id: cam.id,
          url: `rtsp://zlm:554/live/${cam.id}`
        }
        
        if (cam.tasks.includes('presence')) {
          newStreams.occupancy.push({ ...streamData })
        }
        if (cam.tasks.includes('smoking')) {
          // Smoking 也携带 areaCode 以便 AI 引擎统一处理
          newStreams.smoking.push({ ...streamData })
        }
      })
    })

    fullConfig.value.streams = newStreams
    await axios.post('/api/config', fullConfig.value)
    ElMessage.success(t('cameras.saveSuccess'))
  } catch (e) {
    ElMessage.error(t('cameras.saveFailed'))
  }
  loading.value = false
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.area-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('params.title') }}</span>
        <el-button type="primary" @click="saveParams">{{ $t('params.save') }}</el-button>
      </div>
    </template>

    <el-form :model="params" label-width="250px" v-loading="loading">
      
      <el-divider content-position="left">{{ $t('params.mqttConfig') }}</el-divider>
      <el-form-item :label="$t('params.mqttBroker')">
        <el-input v-model="mqttParams.broker" placeholder="例如: 10.0.0.100 或 emqx.io"></el-input>
      </el-form-item>
      <el-form-item :label="$t('params.mqttPort')">
        <el-input-number v-model="mqttParams.port" :min="1" :max="65535"></el-input-number>
      </el-form-item>
      <el-form-item :label="$t('params.mqttKeepalive')">
        <el-input-number v-model="mqttParams.keepalive" :min="10" :max="300"></el-input-number>
      </el-form-item>

      <el-divider content-position="left">{{ $t('params.smokingTitle') }}</el-divider>
      <el-form-item :label="$t('params.poseConf')">
        <el-slider v-model="params.smoking_conf" :min="0" :max="1" :step="0.05" show-input></el-slider>
      </el-form-item>
      <el-form-item :label="$t('params.poseHeuristic')">
        <el-slider v-model="params.pose_heuristic_threshold" :min="0" :max="1" :step="0.05" show-input></el-slider>
      </el-form-item>
      <el-form-item :label="$t('params.smokingSpecConf')">
        <el-slider v-model="params.smoking_specialist_conf" :min="0" :max="1" :step="0.05" show-input></el-slider>
      </el-form-item>

      <el-divider content-position="left">{{ $t('params.occGlobalTitle') }}</el-divider>
      <el-form-item :label="$t('params.maxLogSize')">
        <el-input-number v-model="storageQuota.max_size_mb" :min="100" :max="10240" :step="100"></el-input-number>
        <div class="form-tip">{{ $t('params.maxLogSizeTip') }}</div>
      </el-form-item>

      <el-divider content-position="left">{{ $t('params.occAreasTitle') }}</el-divider>
      <div v-for="(area, index) in areas" :key="index" class="area-card">
        <div class="area-header">
          <span style="font-weight: bold;">{{ $t('params.areaCode') }}: </span>
          <el-input v-model="area.areaCode" style="width: 200px; margin-right: 10px;" placeholder="例如: Floor01/AreaA/Office01"></el-input>
          <el-button type="danger" size="small" @click="removeArea(index)" v-if="areas.length > 1">{{ $t('params.deleteArea') }}</el-button>
        </div>
        <div class="area-body">
          <el-form-item :label="$t('params.scoreThreshold')">
            <el-slider v-model="area.score_threshold" :min="0" :max="1" :step="0.05" show-input style="width: 300px;"></el-slider>
          </el-form-item>
          <el-form-item :label="$t('params.bufferMinutes')">
            <el-input-number v-model="area.buffer_minutes" :min="1" :max="60"></el-input-number>
            <div class="form-tip">{{ $t('params.bufferMinutesTip') }}</div>
          </el-form-item>
          <el-form-item :label="$t('params.level2Minutes')">
            <el-input-number v-model="area.level2_minutes" :min="1" :max="120"></el-input-number>
            <div class="form-tip">{{ $t('params.level2MinutesTip') }}</div>
          </el-form-item>
          <el-form-item :label="$t('params.level3Minutes')">
            <el-input-number v-model="area.level3_minutes" :min="1" :max="120"></el-input-number>
            <div class="form-tip">{{ $t('params.level3MinutesTip') }}</div>
          </el-form-item>
        </div>
      </div>
      <el-button type="primary" plain @click="addArea" style="margin-left: 250px; margin-bottom: 20px;">{{ $t('params.addArea') }}</el-button>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const loading = ref(false)
const fullConfig = ref({})
const params = ref({
  smoking_conf: 0.5,
  occupancy_conf: 0.4,
  state_patience: 120,
  smoking_specialist_conf: 0.25,
  pose_heuristic_threshold: 0.40
})

const mqttParams = ref({
  broker: "buildingos-emqx-prod",
  port: 1883,
  keepalive: 60
})

const storageQuota = ref({
  max_size_mb: 1024
})

const areas = ref([
  {
    areaCode: "Floor01/AreaA/Office01",
    score_threshold: 0.6,
    buffer_minutes: 2,
    level2_minutes: 5,
    level3_minutes: 10
  }
])

const addArea = () => {
  areas.value.push({
    areaCode: "NewArea",
    score_threshold: 0.6,
    buffer_minutes: 2,
    level2_minutes: 5,
    level3_minutes: 10
  })
}

const removeArea = (index) => {
  areas.value.splice(index, 1)
}

const fetchConfig = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/config')
    fullConfig.value = res.data
    if (res.data.model_params) {
      params.value = res.data.model_params
    }
    if (res.data.mqtt) {
      mqttParams.value = res.data.mqtt
    }
    if (res.data.storage_quota) {
      storageQuota.value.max_size_mb = res.data.storage_quota.max_size_mb || 1024
    }
    if (res.data.areas && Array.isArray(res.data.areas)) {
      areas.value = res.data.areas
    }
  } catch (e) {
    ElMessage.error(t('params.fetchFailed'))
  }
  loading.value = false
}

const saveParams = async () => {
  loading.value = true
  try {
    fullConfig.value.model_params = params.value
    fullConfig.value.mqtt = mqttParams.value
    
    if (!fullConfig.value.storage_quota) fullConfig.value.storage_quota = {}
    fullConfig.value.storage_quota.max_size_mb = storageQuota.value.max_size_mb
    
    fullConfig.value.areas = areas.value

    await axios.post('/api/config', fullConfig.value)
    ElMessage.success(t('params.saveSuccess'))
  } catch (e) {
    ElMessage.error(t('params.saveFailed'))
  }
  loading.value = false
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.form-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1.2;
  margin-top: 4px;
}
.area-card {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
  margin-left: 50px;
  background-color: #fcfcfc;
}
.area-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}
</style>

<template>
  <div class="local-model-container">
    <el-card class="box-card inference-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('localModel.title') }}</span>
        </div>
      </template>
      <el-form :model="inferForm" label-width="120px" @submit.prevent>
        <el-form-item :label="$t('localModel.template')">
          <el-select v-model="inferForm.promptTemplate" :placeholder="$t('localModel.templatePlaceholder')" style="width: 100%" @change="onTemplateChange">
            <el-option :label="$t('localModel.descTemplate')" value="Describe this image in detail. Please reply in Chinese. (请详细描述这张图片，用中文回复)" />
            <el-option :label="$t('localModel.smokingTemplate')" value="Is there a person smoking in this image? Answer 'Yes' or 'No' and provide reasons. Please reply in Chinese. (图片中是否有人在抽烟？用中文回复是或否，并说明理由。)" />
            <el-option :label="$t('localModel.helmetTemplate')" value="Are all people in the image wearing safety helmets? Detail any violations. Please reply in Chinese. (图片中所有人是否都佩戴了安全帽？请用中文详细说明违规情况。)" />
            <el-option :label="$t('localModel.presenceTemplate')" value="检测图片中是否有活人存在，仔细鉴别头肩和肢体等人体要输，如果有人回答YES，并且告知在什么位置。没有则回答NO" />
            <el-option :label="$t('localModel.customTemplate')" value="custom" />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="$t('localModel.promptLabel')">
          <el-input 
            type="textarea" 
            v-model="inferForm.prompt" 
            :rows="3" 
            :placeholder="$t('localModel.promptPlaceholder')"
            :disabled="inferForm.promptTemplate !== 'custom'"
          />
        </el-form-item>

        <el-form-item :label="$t('localModel.uploadImage')">
          <el-upload
            class="avatar-uploader"
            action="#"
            :show-file-list="false"
            :auto-upload="false"
            :on-change="handleImageChange"
            accept="image/*"
          >
            <img v-if="inferForm.imageUrl" :src="inferForm.imageUrl" class="avatar" />
            <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
          </el-upload>
        </el-form-item>

        <el-form-item :label="$t('localModel.enableThinking')">
          <el-switch
            v-model="inferForm.enableThinking"
            :active-text="$t('localModel.thinkingYes')"
            :inactive-text="$t('localModel.thinkingNo')"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitInference" :loading="inferring" :disabled="!inferForm.imageUrl">
            {{ $t('localModel.startInference') }}
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="result-section" v-if="inferResult || inferError || inferring">
        <el-divider>{{ $t('localModel.resultDivider') }}</el-divider>
        <el-alert v-if="inferError" :title="inferError" type="error" show-icon :closable="false" />
        <div v-else-if="inferring" class="loading-state">
          <el-skeleton :rows="5" animated />
        </div>
        <div v-else class="result-container">
          <!-- Final Result (Categorized) -->
          <div :class="['result-box', inferResult === 'YES' ? 'occupied' : inferResult === 'NO' ? 'empty' : '']">
            <div class="result-label">RESULT: {{ inferResult }}</div>
            <div class="analysis-content">{{ inferReasoning }}</div>
          </div>

          <!-- Raw LLM Response -->
          <el-collapse class="raw-collapse">
            <el-collapse-item name="1">
              <template #title>
                <el-icon class="header-icon"><Cpu /></el-icon> LLM Raw JSON Response
              </template>
              <div class="raw-content">
                <pre>{{ inferRawResponse }}</pre>
              </div>
            </el-collapse-item>
          </el-collapse>

          <!-- Metrics Footer -->
          <div v-if="inferMetrics" class="metrics-footer">
            <div class="metric-item">
              <el-icon><Timer /></el-icon>
              <span>{{ inferMetrics.durationStr }}</span>
            </div>
            <div class="metric-item">
              <el-icon><Document /></el-icon>
              <span>{{ inferMetrics.contextStr }}</span>
            </div>
            <div class="metric-item">
              <el-icon><Aim /></el-icon>
              <span>{{ inferMetrics.outputStr }}</span>
            </div>
            <div class="metric-item">
              <el-icon><Odometer /></el-icon>
              <span>{{ inferMetrics.speedStr }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Cpu, Aim, Odometer, Document, Timer } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const inferring = ref(false)
const inferResult = ref('')
const inferReasoning = ref('')
const inferRawResponse = ref('')
const inferMetrics = ref(null)
const inferError = ref('')

const inferForm = ref({
  promptTemplate: 'Describe this image in detail. Please reply in Chinese. (请详细描述这张图片，用中文回复)',
  prompt: 'Describe this image in detail. Please reply in Chinese. (请详细描述这张图片，用中文回复)',
  imageUrl: '',
  imageBase64: '',
  enableThinking: false
})

const onTemplateChange = (val) => {
  if (val !== 'custom') {
    inferForm.value.prompt = val
  } else {
    inferForm.value.prompt = ''
  }
}

const handleImageChange = (file) => {
  const rawFile = file.raw
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error(t('localModel.onlyImageError'))
    return false
  }
  
  // Create a local URL for preview
  inferForm.value.imageUrl = URL.createObjectURL(rawFile)
  
  // Convert to Base64 for API
  const reader = new FileReader()
  reader.readAsDataURL(rawFile)
  reader.onload = () => {
    inferForm.value.imageBase64 = reader.result
  }
}

const submitInference = async () => {
  if (!inferForm.value.imageBase64) {
    ElMessage.warning(t('localModel.uploadRequired'))
    return
  }
  if (!inferForm.value.prompt) {
    ElMessage.warning(t('localModel.promptRequired'))
    return
  }

  inferring.value = true
  inferResult.value = ''
  inferReasoning.value = ''
  inferRawResponse.value = ''
  inferMetrics.value = null
  inferError.value = ''

  try {
    const res = await axios.post('/api/gemma/infer', {
      image: inferForm.value.imageBase64,
      prompt: inferForm.value.prompt,
      enableThinking: inferForm.value.enableThinking
    })
    
    if (res.data.error) {
      inferError.value = res.data.error + (res.data.details ? `: ${res.data.details}` : '')
    } else {
      inferResult.value = res.data.result
      inferReasoning.value = res.data.reasoning
      inferRawResponse.value = res.data.llm_response
      
      // Calculate metrics if available
      if (res.data.usage && res.data.timings) {
        const promptTokens = res.data.usage.prompt_tokens || 0
        const totalContext = 4096 // Typical context size, adjust if needed
        const contextPercent = Math.round((promptTokens / totalContext) * 100)
        
        const predictedTokens = res.data.timings.predicted_n || 0
        const tokensPerSecond = (res.data.timings.predicted_per_second || 0).toFixed(1)
        const durationSec = ((res.data.durationMs || 0) / 1000).toFixed(2)
        
        inferMetrics.value = {
          contextStr: `Context: ${promptTokens}/${totalContext} (${contextPercent}%)`,
          outputStr: `Output: ${predictedTokens}/∞`,
          speedStr: `${tokensPerSecond} t/s`,
          durationStr: `Time: ${durationSec} s`
        }
      }
    }
  } catch (err) {
    inferError.value = err.response?.data?.error || err.message || '推理请求失败'
  } finally {
    inferring.value = false
  }
}

onMounted(() => {
  // fetchStatus() removed
})
</script>

<style scoped>
.local-model-container {
  padding: 20px;
}
.box-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.status-tag {
  font-size: 14px;
  padding: 4px 10px;
}
.status-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
  object-fit: cover;
  border-radius: 6px;
}

.result-section {
  margin-top: 30px;
}

.result-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.reasoning-collapse {
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
}

.reasoning-collapse :deep(.el-collapse-item__header) {
  padding-left: 15px;
  background-color: #fafafa;
  color: #606266;
  font-weight: bold;
}

.header-icon {
  margin-right: 8px;
  font-size: 16px;
}

.reasoning-content {
  padding: 15px;
  background-color: #fff;
  border-top: 1px solid var(--el-border-color-lighter);
}

.reasoning-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #909399;
  font-family: monospace;
  line-height: 1.5;
  font-size: 13px;
}

.result-box {
  background-color: #f0f9eb;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #e1f3d8;
  color: #303133;
  line-height: 1.6;
}

.result-box.occupied {
  background-color: #fef0f0;
  border-color: #fde2e2;
  color: #f56c6c;
}

.result-box.empty {
  background-color: #f0f9eb;
  border-color: #e1f3d8;
  color: #67c23a;
}

.result-label {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 8px;
  border-bottom: 1px dashed rgba(0,0,0,0.1);
  padding-bottom: 5px;
}

.analysis-content {
  font-size: 14px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.raw-collapse {
  margin-top: 10px;
}

.raw-content {
  padding: 10px;
  background-color: #303133;
  color: #fff;
  border-radius: 4px;
}

.raw-content pre {
  margin: 0;
  font-size: 11px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.metrics-footer {
  display: flex;
  justify-content: flex-start;
  gap: 30px;
  margin-top: 5px;
  padding-top: 10px;
  border-top: 1px solid #ebeef5;
  color: #909399;
  font-size: 12px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.loading-state {
  padding: 20px;
}
</style>

<template>
  <el-card class="box-card heatmap-card">
    <template #header>
      <div class="card-header">
        <span><el-icon><Calendar /></el-icon> {{ $t('logs.heatmapTitle') }}</span>
        <div class="header-buttons">
          <el-button @click="dialogTestVisible = true" type="warning" plain size="small" :icon="Picture">{{ $t('logs.testButton') }}</el-button>
          <el-button @click="fetchLogs" type="primary" plain size="small" :icon="Search" :loading="loading">{{ $t('logs.refreshButton') }}</el-button>
        </div>
      </div>
    </template>

    <div class="filter-section">
      <el-select v-model="selectedArea" :placeholder="$t('logs.selectAreaPlaceholder')" style="width: 250px; margin-right: 15px;" filterable>
        <el-option v-for="area in uniqueAreas" :key="area" :label="area" :value="area"></el-option>
      </el-select>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        :range-separator="$t('logs.dateRangeSeparator')"
        :start-placeholder="$t('logs.startDatePlaceholder')"
        :end-placeholder="$t('logs.endDatePlaceholder')"
        value-format="YYYY-MM-DD"
        @change="handleFilterChange"
        style="width: 300px; margin-right: 15px;"
      />
      
      <!-- Auto refresh switch -->
      <el-switch
        v-model="autoRefresh"
        :active-text="$t('logs.autoRefreshOn')"
        :inactive-text="$t('logs.autoRefreshOff')"
        @change="toggleAutoRefresh"
        style="margin-right: 15px;"
      />

      <div class="legend">
        <span style="margin-right: 10px;">{{ $t('logs.legendNoRecord') }}</span>
        <ul class="legend-colors">
          <li class="color-level-null"></li>
        </ul>
        <span style="margin-right: 10px;">{{ $t('logs.legendEmpty') }}</span>
        <ul class="legend-colors">
          <li class="color-level-0"></li>
          <li class="color-level-1"></li>
          <li class="color-level-2"></li>
          <li class="color-level-3"></li>
          <li class="color-level-4"></li>
        </ul>
        <span>{{ $t('logs.legendOccupied') }}</span>
      </div>
    </div>

    <div v-loading="loading" class="heatmaps-wrapper">
      <div v-if="!selectedArea" class="no-data">
        <el-empty :description="$t('logs.selectAreaTip')"></el-empty>
      </div>
      <div v-else-if="displayDays.length === 0" class="no-data">
        <el-empty :description="$t('logs.noDataTip')"></el-empty>
      </div>
      
      <!-- 左右两块布局，一行两天 -->
      <el-row :gutter="40" v-else>
        <el-col :span="12" v-for="dayData in displayDays" :key="dayData.date" style="margin-bottom: 40px;">
          <div class="day-heatmap">
            <div class="day-header">
              <h4 class="day-title">{{ dayData.date }}</h4>
              <el-button 
                v-if="summaries[dayData.date]" 
                type="primary" 
                link 
                size="small" 
                class="summary-link"
                @click="openSummary(dayData.date)"
              >
                <el-icon><Document /></el-icon> {{ $t('logs.viewDailySummary') }}
              </el-button>
            </div>
            <div class="heatmap-container">
              <!-- Y-axis (Minutes): 50m at top, 0m at bottom -->
              <div class="y-axis-wrapper">
                <div class="y-axis">
                  <div class="y-label" v-for="m in 6" :key="m">
                    <span>{{ (6 - m) * 10 }}m</span>
                  </div>
                </div>
                <div class="x-axis-placeholder"></div>
              </div>
              
              <!-- Grid -->
              <div class="grid-content">
                 <div class="grid-columns">
                    <div class="column" v-for="hour in 24" :key="hour">
                       <!-- 反转 minuteIdx 渲染顺序，使 DOM 节点也自下而上排列 0m, 10m...50m -->
                       <el-tooltip
                          v-for="minuteIdx in 6" :key="minuteIdx"
                          placement="top"
                          :content="getTooltip(dayData, hour-1, 6 - minuteIdx)"
                          :show-after="200"
                       >
                         <div 
                            class="cell" 
                            :class="getCellIntensityClass(dayData, hour-1, 6 - minuteIdx)"
                            @click="openDetail(dayData, hour-1, 6 - minuteIdx)"
                         ></div>
                       </el-tooltip>
                    </div>
                 </div>
                 <!-- X-axis (Hours) -->
                 <div class="x-axis">
                   <div class="x-label" v-for="hour in 24" :key="hour">{{ (hour - 1).toString().padStart(2, '0') }}:00</div>
                 </div>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>

    <!-- AI 日报总结弹窗 -->
    <el-dialog v-model="summaryDialogVisible" :title="$t('logs.summaryDialogTitle', { date: selectedDate })" width="700px">
      <div v-if="selectedSummary" class="summary-content">
        <el-descriptions :column="1" border size="small" class="summary-stats">
          <el-descriptions-item :label="$t('logs.summaryGeneratedAt')">
            {{ formatTime(selectedSummary.generated_at) }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('logs.summaryOverview')">
            <el-tag size="small">{{ $t('logs.summaryTotalSamples') }}: {{ selectedSummary.stats.summary_stats.total_samples }}</el-tag>
            <el-tag size="small" type="success" style="margin-left: 5px;">{{ $t('logs.summaryLvl1Direct') }}: {{ selectedSummary.stats.summary_stats.lvl1_direct_confirm }}</el-tag>
            <el-tag size="small" type="warning" style="margin-left: 5px;">{{ $t('logs.summaryLvl2Reviews') }}: {{ selectedSummary.stats.summary_stats.lvl2_gemma_reviews }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('logs.summaryReviewResult')">
            <span style="color: #67C23A">{{ $t('logs.summaryOccupiedConfirmed') }}: {{ selectedSummary.stats.summary_stats.lvl2_gemma_confirmed }}</span>
            <span style="color: #F56C6C; margin-left: 15px;">{{ $t('logs.summaryFalseAlarmDenied') }}: {{ selectedSummary.stats.summary_stats.lvl2_gemma_denied }}</span>
          </el-descriptions-item>
        </el-descriptions>

        <div class="summary-text-box">
          <div class="summary-label">{{ $t('logs.summaryGemmaReport') }}</div>
          <div class="summary-markdown" v-html="renderMarkdown(selectedSummary.summary)"></div>
        </div>

        <div v-if="selectedSummary.stats.areas[selectedArea]?.lvl2_details?.length > 0" class="summary-details">
          <div class="summary-label">{{ $t('logs.summaryTimelineTitle', { area: selectedArea }) }}</div>
          <el-table :data="selectedSummary.stats.areas[selectedArea].lvl2_details" size="small" border stripe style="margin-top: 10px;">
            <el-table-column prop="time" :label="$t('logs.summaryTableTime')" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.time) }}
              </template>
            </el-table-column>
            <el-table-column prop="res" :label="$t('logs.summaryTableResult')" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.res === 'YES' ? 'success' : 'danger'" size="small">
                  {{ scope.row.res === 'YES' ? $t('logs.statusOccupied') : $t('logs.statusEmpty') }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" :label="$t('logs.summaryTableChain')">
              <template #default="scope">
                <span style="font-size: 11px; color: #909399;">{{ scope.row.reason.join(' → ') }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 详情弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="1000px" top="5vh">
      <div v-if="dialogLogs.length === 0">
        <el-empty :description="$t('logs.noRecordTip')"></el-empty>
      </div>
      <el-timeline v-else>
        <el-timeline-item
          v-for="group in groupedLogs"
          :key="group.time"
          :timestamp="group.time"
          :type="group.logs.some(l => l.raw_payload?.result === 'occupied') ? 'success' : 'info'"
        >
          <el-card shadow="hover" class="log-detail-card">
            <div class="log-header">
              <el-tag :type="getGroupResultTagType(group)" size="small" effect="dark">
                {{ formatGroupResult(group) }}
              </el-tag>
              <span class="log-event">{{ $t('logs.statusUpdate') }}</span>
            </div>
            
            <div class="log-meta" style="margin-top: 10px; font-size: 13px; color: #606266;">
              <p><strong>{{ $t('logs.strategyChain') }}</strong> {{ getStrategyChain(group) }}</p>
              <p style="margin-top: 5px;">
                <strong>{{ $t('logs.finalDecision') }}</strong> 
                <el-popover placement="bottom" :title="$t('logs.decisionProcessTitle')" width="400" trigger="click">
                  <template #reference>
                    <el-link type="primary" :underline="false">1-minute sample ({{ $t('logs.clickToView') }})</el-link>
                  </template>
                  <div style="font-size: 13px;">
                    <p v-for="log in group.logs" :key="log.id" style="margin-bottom: 5px;">
                      <b><el-icon><VideoCamera /></el-icon> {{ log.camera_id }}:</b> 
                      <span v-if="log.raw_payload?.result === 'occupied'" style="color: #67C23A; margin-left: 5px;">{{ $t('logs.decidedOccupied') }}</span>
                      <span v-else style="color: #909399; margin-left: 5px;">{{ $t('logs.decidedEmpty') }}</span>
                      <span style="margin-left: 5px; color: #E6A23C;" v-if="log.raw_payload?.yolo_count > 0">({{ $t('logs.detectedCount', { count: log.raw_payload?.yolo_count }) }})</span>
                    </p>
                    <el-divider style="margin: 10px 0;"></el-divider>
                    <p><b>{{ $t('logs.areaSummaryResult') }}</b> 
                      <span v-if="group.logs.some(l => l.raw_payload?.result === 'occupied')" style="color: #67C23A; font-weight: bold;">{{ $t('logs.areaOccupied') }}</span>
                      <span v-else style="color: #909399; font-weight: bold;">{{ $t('logs.areaEmpty') }}</span>
                    </p>
                  </div>
                </el-popover>
              </p>
            </div>

            <div style="margin-top: 15px; font-size: 13px; font-weight: bold; color: #303133; margin-bottom: 10px;">
              {{ $t('logs.evidenceTitle') }}
            </div>
            
            <!-- 多摄像头左右排列 -->
            <el-row :gutter="15">
              <el-col :span="24 / Math.min(group.logs.length, 4)" v-for="log in group.logs" :key="log.id">
                <div class="camera-evidence">
                  <p style="font-weight: bold; margin-bottom: 5px; color: #409EFF; font-size: 13px; display: flex; justify-content: space-between;">
                    <span><el-icon><VideoCamera /></el-icon> {{ log.camera_id }}</span>
                    <el-tag size="small" type="info" effect="plain" v-if="log.detector_type || log.raw_payload?.detector_type">
                      {{ log.detector_type || log.raw_payload?.detector_type }}
                    </el-tag>
                  </p>
                  <!-- 显示第一张图（也就是带有时间戳和红框的 annotated_frame） -->
                  <el-image 
                    v-if="log.images && log.images.length > 0"
                    :src="`${getImageUrl(log.images[0])}?t=${new Date().getTime()}`" 
                    :preview-src-list="log.images.map(i => getImageUrl(i))"
                    :initial-index="0"
                    fit="contain"
                    class="log-image"
                  />
                  <div class="evidence-chain" style="margin-top: 10px; font-size: 12px; color: #606266; background: #f5f7fa; padding: 8px; border-radius: 4px; min-height: 80px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                      <b style="color: #303133;">{{ $t('logs.evidenceChainTitle') }}</b>
                      <el-link type="info" :underline="false" style="font-size: 11px;" @click="viewRawJson(log)">
                        [{{ $t('logs.viewRawJson') }}]
                      </el-link>
                    </div>
                    <ul style="padding-left: 20px; margin-top: 5px; margin-bottom: 0;">
                      <li v-for="(step, idx) in (log.raw_payload?.decision_chain || [$t('logs.noLogChain')])" :key="idx" style="margin-bottom: 3px;">
                        <span v-if="step.includes('Gemma 复核')">
                          {{ translateChainStep(step) }}
                          <el-link type="primary" size="small" @click="handleManualGemmaReview(log)" :loading="manualReviewing === log.id" style="margin-left: 5px; font-size: 11px;">
                            [{{ $t('logs.manualReviewButton') }}]
                          </el-link>
                        </span>
                        <span v-else>{{ translateChainStep(step) }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </el-col>
            </el-row>
          </el-card>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>

    <!-- 算法验证单图测试弹窗 -->
    <el-dialog v-model="dialogTestVisible" :title="$t('logs.testDialogTitle')" width="800px" destroy-on-close>
      <div class="test-container">
        <el-row :gutter="20">
          <el-col :span="10">
            <el-form :model="testForm" label-position="top">
              <el-form-item :label="$t('logs.uploadTestImage')">
                <el-upload
                  class="test-uploader"
                  action="#"
                  :show-file-list="false"
                  :auto-upload="false"
                  :on-change="handleTestImageChange"
                  accept="image/*"
                >
                  <img v-if="testForm.imageUrl" :src="testForm.imageUrl" class="test-preview-img" />
                  <div v-else class="test-uploader-placeholder">
                    <el-icon class="test-uploader-icon"><Plus /></el-icon>
                    <span>{{ $t('logs.clickToUpload') }}</span>
                  </div>
                </el-upload>
              </el-form-item>
              
              <el-form-item :label="$t('logs.confThres')">
                <el-slider v-model="testForm.conf_thres" :min="0.01" :max="0.99" :step="0.01" show-input />
                <div class="form-tip">{{ $t('logs.confThresTip') }}</div>
              </el-form-item>

              <el-form-item>
                <el-button type="primary" @click="submitTest" :loading="testing" :disabled="!testForm.imageBase64" style="width: 100%">
                  {{ $t('logs.startTestInference') }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-col>
          
          <el-col :span="14">
            <div class="test-result-section">
              <div v-if="testing" class="test-loading">
                <el-skeleton :rows="8" animated />
              </div>
              <div v-else-if="testResult" class="test-result-content">
                <div class="result-title">{{ $t('logs.testVisualTitle') }}</div>
                <el-image 
                  :src="testResult.annotated_image" 
                  :preview-src-list="[testResult.annotated_image]"
                  fit="contain" 
                  class="test-result-img"
                />
                
                <div class="result-stats">
                  <el-tag size="small" type="info">{{ $t('logs.testDetector') }} {{ testResult.detector_source }}</el-tag>
                  <el-tag size="small" type="success" style="margin-left: 10px;">{{ $t('logs.testDetectedTargets', { count: testResult.results.length }) }}</el-tag>
                </div>

                <div class="result-list" style="margin-top: 15px;">
                  <el-table :data="testResult.results" size="small" border height="150">
                    <el-table-column prop="class_name" :label="$t('logs.testTableClass')" width="100" />
                    <el-table-column prop="conf" :label="$t('logs.testTableConf')" width="100">
                      <template #default="scope">
                        {{ (scope.row.conf * 100).toFixed(1) }}%
                      </template>
                    </el-table-column>
                    <el-table-column :label="$t('logs.testTableBbox')">
                      <template #default="scope">
                        {{ scope.row.bbox.join(', ') }}
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
              <el-empty v-else :description="$t('logs.testWaitingTip')"></el-empty>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted, watch as vueWatch } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus'
import { Calendar, VideoCamera, Plus, Picture, Search, Document } from '@element-plus/icons-vue'
import { marked } from 'marked'

const { t } = useI18n()
const loading = ref(false)
const allLogs = ref([])
const areaList = ref([]) // 存储场景列表
const selectedArea = ref('')
const dateRange = ref([])
const autoRefresh = ref(false)
let refreshInterval = null

const dialogVisible = ref(false)
const dialogTitle = ref('')
const dialogLogs = ref([])

const viewRawJson = (log) => {
  ElMessageBox.alert(
    `<pre style="background: #303133; color: #fff; padding: 15px; border-radius: 4px; font-size: 12px; overflow: auto; max-height: 500px;">${JSON.stringify(log, null, 2)}</pre>`,
    t('logs.rawJsonTitle'),
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: t('logs.close'),
      width: '700px'
    }
  )
}

// --- Summary State ---
const summaryDialogVisible = ref(false)
const summaries = ref({})
const selectedDate = ref('')
const selectedSummary = ref(null)

const openSummary = (date) => {
  selectedDate.value = date
  selectedSummary.value = summaries.value[date]
  summaryDialogVisible.value = true
}

const renderMarkdown = (text) => {
  if (!text) return ''
  return marked(text)
}

const fetchSummary = async (date) => {
  try {
    const res = await axios.get(`/api/occupancy/summary/${date}`)
    summaries.value[date] = res.data
  } catch (e) {
    // If not found, ignore
  }
}
// ----------------------

// --- Test Image State ---
const dialogTestVisible = ref(false)
const testing = ref(false)
const testResult = ref(null)
const testForm = ref({
  imageUrl: '',
  imageBase64: '',
  conf_thres: 0.25
})

const handleTestImageChange = (file) => {
  const rawFile = file.raw
  if (!rawFile.type.startsWith('image/')) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  
  testForm.value.imageUrl = URL.createObjectURL(rawFile)
  
  const reader = new FileReader()
  reader.readAsDataURL(rawFile)
  reader.onload = () => {
    testForm.value.imageBase64 = reader.result
  }
}

const submitTest = async () => {
  if (!testForm.value.imageBase64) return
  
  testing.value = true
  testResult.value = null
  
  try {
    const res = await axios.post('/api/ai/test', {
      image: testForm.value.imageBase64,
      conf_thres: testForm.value.conf_thres
    })
    testResult.value = res.data
  } catch (e) {
    ElMessage.error(e.response?.data?.error || t('logs.testRequestFailed'))
  } finally {
    testing.value = false
  }
}
// -------------------------

const manualReviewing = ref('')

const translateChainStep = (step) => {
  if (!step) return step
  
  // 1. Detector 检测到 X 个候选人员
  let match = step.match(/(Detector|RF-DETR|YOLO) 检测到 (\d+) 个候选人员/)
  if (match) return t('chain.detectorDetected', { count: match[2] })

  // 2. Detector 高置信度(X)直接确认有人
  match = step.match(/(Detector|RF-DETR|YOLO) 高置信度\(([\d.]+)\)直接确认有人/)
  if (match) return t('chain.detectorHighConf', { conf: match[2] })

  // 3. Detector 未检测到人员，准备全图复核
  match = step.match(/(Detector|RF-DETR|YOLO) 未检测到人员，准备全图复核/)
  if (match) return t('chain.detectorNotFound', { name: match[1] })

  // 3. Gemma 二级裁决结果: YES/NO
  match = step.match(/Gemma 二级裁决结果: (\w+)/)
  if (match) return t('chain.gemmaL2Result', { res: match[1] })

  // 4. 固定短语匹配
  const directMap = {
    "Gemma 复核: 确认图中存在真实人员": "chain.gemmaConfirmed",
    "Gemma 复核: Detector漏报，但Gemma在全图中发现了人员": "chain.gemmaMissedButFound",
    "Gemma 复核: 否决 (认定疑似目标为误报/假人)": "chain.gemmaDenied",
    "Gemma 复核: 确认全图确实无人": "chain.gemmaConfirmedEmpty",
    "Gemma 响应异常，降级采信 Detector 结果: YES": "chain.gemmaExceptionYes",
    "Gemma 响应异常，降级采信 Detector 结果: NO": "chain.gemmaExceptionNo",
    "图像编码失败，降级采信 Detector": "chain.encodingFailed",
    "AI 引擎默认状态更新": "chain.defaultUpdate",
    "直接采信无日志": "logs.noLogChain"
  }

  return directMap[step] ? t(directMap[step]) : step
}

const handleManualGemmaReview = async (log) => {
  if (!log.images || log.images.length === 0) return
  
  manualReviewing.value = log.id
  const loadingInstance = ElLoading.service({
    lock: true,
    text: t('logs.manualReviewingLoading'),
    background: 'rgba(0, 0, 0, 0.7)',
  })

  try {
    // 1. 获取原始图片 (如果是[annotated, original]，则选第二个；否则选第一个)
    const imageUrl = getImageUrl(log.images[1] || log.images[0])
    
    // 2. 将图片转换为 Base64
    const response = await fetch(imageUrl)
    const blob = await response.blob()
    const reader = new FileReader()
    const base64Promise = new Promise((resolve) => {
      reader.onloadend = () => resolve(reader.result)
      reader.readAsDataURL(blob)
    })
    const imageBase64 = await base64Promise

    // 3. 调用后端复核接口
    const prompt = "检测图片中是否有活人存在，仔细鉴别头肩和肢体等人体要输，如果有人回答YES，并且告知在什么位置。没有则回答NO"
    
    const res = await axios.post('/api/gemma/infer', {
      image: imageBase64,
      prompt: prompt,
      enableThinking: false // 自动 JSON 模式不需要思维链显示
    })

    const { result, reasoning, prompt: sentPrompt, llm_response } = res.data
    
    ElMessageBox.alert(
      `<div style="font-size: 14px;">
        <p><b>${t('logs.manualReviewResultTitle')}</b> <span style="color: ${result === 'YES' ? '#67C23A' : '#F56C6C'}; font-weight: bold;">${result}</span></p>
        <p style="margin-top: 10px;"><b>${t('logs.manualReviewReasoningTitle')}</b></p>
        <div style="background: #f5f7fa; padding: 10px; border-radius: 4px; font-size: 12px; color: #606266; max-height: 150px; overflow-y: auto; margin-bottom: 10px;">
          ${reasoning || t('logs.none')}
        </div>
        <p><b>LLM Raw Response:</b></p>
        <pre style="background: #303133; color: #fff; padding: 10px; border-radius: 4px; font-size: 11px; overflow-x: auto;">${llm_response}</pre>
      </div>`,
      t('logs.manualReviewDialogTitle'),
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: t('logs.close'),
        width: '600px'
      }
    )
  } catch (e) {
    ElMessage.error(t('logs.manualReviewFailed') + (e.response?.data?.error || e.message))
  } finally {
    manualReviewing.value = ''
    loadingInstance.close()
  }
}

const toggleAutoRefresh = (val) => {
  if (val) {
    ElMessage.success(t('logs.autoRefreshStarted'))
    fetchLogs(true)
    refreshInterval = setInterval(() => fetchLogs(true), 60000)
  } else {
    if (refreshInterval) clearInterval(refreshInterval)
    ElMessage.info(t('logs.autoRefreshStopped'))
  }
}

// 默认显示最近4天（包含今天）
const getDefaultDateRange = () => {
  const dates = []
  for (let i = 0; i < 4; i++) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    dates.push(`${year}-${month}-${day}`)
  }
  return dates
}

const defaultDates = ref(getDefaultDateRange())

const fetchAreas = async () => {
  try {
    const res = await axios.get('/api/occupancy/areas')
    areaList.value = res.data || []
  } catch (e) {
    console.error("Failed to fetch areas:", e)
  }
}

const fetchLogs = async (silent = false) => {
  if (!silent) loading.value = true
  try {
    // 如果没有选定场景，不请求日志，只请求场景列表
    if (!selectedArea.value) {
      await fetchAreas()
      if (!silent) loading.value = false
      return
    }

    const params = { days: 4, areaCode: selectedArea.value }
    const res = await axios.get('/api/occupancy/logs', { params })
    allLogs.value = (res.data || []).filter(l => l.camera_id && l.areaCode && l.areaCode !== 'UNKNOWN')
    
    defaultDates.value.forEach(date => {
      fetchSummary(date)
    })
  } catch (e) {
    if (!silent) ElMessage.error(t('logs.fetchLogsFailed'))
  }
  if (!silent) loading.value = false
}

// 核心：按选定日期和场景，生成二维热力图数据
const displayDays = computed(() => {
  if (!selectedArea.value) return []

  let datesToDisplay = []
  if (dateRange.value && dateRange.value.length === 2) {
    const start = new Date(dateRange.value[0])
    const end = new Date(dateRange.value[1])
    for (let d = new Date(end); d >= start; d.setDate(d.getDate() - 1)) {
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      datesToDisplay.push(`${year}-${month}-${day}`)
    }
  } else {
    datesToDisplay = defaultDates.value
  }

  const result = []
  const areaLogs = allLogs.value.filter(log => log.areaCode === selectedArea.value)

  datesToDisplay.forEach(dateStr => {
    // 根据 dateStr 获取该日期的边界，过滤掉未来的时间点
    const todayStr = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '-')
    const isToday = dateStr === todayStr
    const currentHour = new Date().getHours()
    const currentMin = new Date().getMinutes()

    // 匹配特定日期的日志 (使用 log.date 而非 log.timestamp 解析，避免跨时区导致日期漂移)
    const dayLogs = areaLogs.filter(log => log.date === dateStr)
    
    if (dayLogs.length > 0 || datesToDisplay.length <= 4) {
      const grid = Array.from({ length: 24 }, () => Array.from({ length: 6 }, () => []))
      
      dayLogs.forEach(log => {
        if (!log.timestamp) return
        let d = new Date(log.timestamp)
        const hour = d.getHours()
        const min = d.getMinutes()
        const minIdx = Math.floor(min / 10)
        
        // 过滤掉超过当前时间点的未来数据
        if (isToday) {
            if (hour > currentHour || (hour === currentHour && min > currentMin)) {
                return 
            }
        }

        if (hour >= 0 && hour < 24 && minIdx >= 0 && minIdx < 6) {
          grid[hour][minIdx].push(log)
        }
      })
      
      result.push({
        date: dateStr,
        grid: grid
      })
    }
  })
  
  return result
})

const getCellLogs = (dayData, hour, minuteIdx) => {
  return dayData.grid[hour][minuteIdx] || []
}

const getCellIntensityClass = (dayData, hour, minuteIdx) => {
  const logs = getCellLogs(dayData, hour, minuteIdx)
  if (logs.length === 0) return 'color-level-null'
  
  const occupiedLogs = logs.filter(l => l.raw_payload?.result === 'occupied')
  if (occupiedLogs.length === 0) return 'color-level-0'
  
  const count = occupiedLogs.length
  if (count === 1) return 'color-level-1'
  if (count === 2) return 'color-level-2'
  if (count === 3) return 'color-level-3'
  return 'color-level-4'
}

const getTooltip = (dayData, hour, minuteIdx) => {
  const logs = getCellLogs(dayData, hour, minuteIdx)
  const timeStr = `${hour.toString().padStart(2, '0')}:${(minuteIdx * 10).toString().padStart(2, '0')} - ${hour.toString().padStart(2, '0')}:${(minuteIdx * 10 + 9).toString().padStart(2, '0')}`
  if (logs.length === 0) return `${timeStr} ${t('logs.noDetectionRecord')}`
  
  const occupiedLogs = logs.filter(l => l.raw_payload?.result === 'occupied')
  return `${timeStr} | ${t('logs.statusOccupied')}: ${occupiedLogs.length}次, ${t('logs.summaryTotalSamples')}: ${logs.length}次`
}

// 提取并聚合多摄像头的按分钟日志
const groupedLogs = computed(() => {
  const groups = {}
  dialogLogs.value.forEach(log => {
    if (!log.timestamp) return
    const d = new Date(log.timestamp)
    const minKey = `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
    if (!groups[minKey]) groups[minKey] = []
    groups[minKey].push(log)
  })
  
  return Object.keys(groups).sort((a, b) => new Date(b) - new Date(a)).map(k => ({
    time: k,
    logs: groups[k]
  }))
})

const getGroupResultTagType = (group) => {
  const isOccupied = group.logs.some(l => l.raw_payload?.result === 'occupied')
  return isOccupied ? 'success' : 'info'
}

const getStrategyChain = (group) => {
  if (!group.logs || group.logs.length === 0) return 'Object detection+Gemma'
  const log = group.logs[0]
  const detector = log.detector_type || log.raw_payload?.detector_type || 'Detector'
  return `${detector}+Gemma`
}

const formatGroupResult = (group) => {
  const isOccupied = group.logs.some(l => l.raw_payload?.result === 'occupied')
  return isOccupied ? t('logs.areaOccupied') : t('logs.areaEmpty')
}

const openDetail = (dayData, hour, minuteIdx) => {
  const logs = getCellLogs(dayData, hour, minuteIdx)
  if (logs.length === 0) return
  
  const timeStr = `${hour.toString().padStart(2, '0')}:${(minuteIdx * 10).toString().padStart(2, '0')} - ${hour.toString().padStart(2, '0')}:${(minuteIdx * 10 + 9).toString().padStart(2, '0')}`
  dialogTitle.value = `[${selectedArea.value}] ${dayData.date} ${timeStr} ${t('logs.detailRecordTitle')}`
  dialogLogs.value = [...logs].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  dialogVisible.value = true
}

const formatTime = (isoString) => {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleTimeString()
}

const getImageUrl = (relativePath) => {
  return `http://${window.location.hostname}:10081/${relativePath}`
}

const handleFilterChange = () => {
  fetchLogs()
}

const uniqueAreas = computed(() => {
  if (areaList.value.length > 0) return areaList.value
  const areas = new Set(allLogs.value.map(l => l.areaCode))
  return Array.from(areas).sort()
})

// 监听选择场景的变化，自动重新加载数据
vueWatch(selectedArea, () => {
  fetchLogs()
})

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.heatmap-card {
  min-height: 800px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
.filter-section {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}
.legend {
  display: flex;
  align-items: center;
  margin-left: auto;
  font-size: 12px;
  color: #606266;
}
.legend-colors {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 0 8px;
  gap: 4px;
}
.legend-colors li {
  width: 14px;
  height: 14px;
  border-radius: 3px;
}

/* Element Plus Primary Blue Theme Heatmap Colors */
.color-level-null { background-color: #ebedf0; } /* 根本没日志（未来时间，断网等） */
.color-level-0 { background-color: #f4f4f5; }    /* 有判断日志，但是判定为无人 */
.color-level-1 { background-color: #c6e2ff; }
.color-level-2 { background-color: #79bbff; }
.color-level-3 { background-color: #409eff; }
.color-level-4 { background-color: #337ecc; }

.heatmaps-wrapper {
  display: flex;
  flex-direction: column;
  gap: 40px;
}
.day-heatmap {
  display: flex;
  flex-direction: column;
}
.day-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-left: 45px;
}
.day-title {
  margin: 0;
  font-size: 14px;
  color: #303133;
  font-weight: bold;
}
.summary-link {
  font-size: 12px;
}
.summary-content {
  padding: 10px;
}
.summary-stats {
  margin-bottom: 20px;
}
.summary-text-box {
  background: #f4f4f5;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #909399;
  margin-bottom: 20px;
}
.summary-label {
  font-weight: bold;
  margin-bottom: 12px;
  color: #303133;
  font-size: 15px;
}
.summary-markdown {
  line-height: 1.6;
  color: #606266;
  font-size: 14px;
}
.summary-markdown :deep(h1), 
.summary-markdown :deep(h2), 
.summary-markdown :deep(h3) {
  margin-top: 15px;
  margin-bottom: 10px;
  color: #303133;
}
.summary-markdown :deep(ul), 
.summary-markdown :deep(ol) {
  padding-left: 20px;
  margin-bottom: 10px;
}
.summary-markdown :deep(li) {
  margin-bottom: 5px;
}
.summary-markdown :deep(p) {
  margin-bottom: 10px;
}
.summary-markdown :deep(strong) {
  color: #303133;
}
.summary-details {
  margin-top: 20px;
}
.heatmap-container {
  display: flex;
  align-items: flex-start;
  width: 100%;
}
.y-axis-wrapper {
  display: flex;
  flex-direction: column;
  margin-right: 15px;
  width: 30px;
}
.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 4px; /* Matches grid gap */
}
.y-label {
  font-size: 10px;
  color: #909399;
  line-height: 1;
  text-align: right;
  /* Make label height match cell height proportionally */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  /* Use aspect-ratio to match square cells if needed, 
     but since they are in flex-column, we just need them to share the space */
  flex: 1;
  padding-bottom: 100%; /* Force labels to have same aspect ratio as cells */
  position: relative;
}
.y-label span {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 0;
}
.x-axis-placeholder {
  height: 21px; /* Matches x-axis height + margin */
}
.grid-content {
  display: flex;
  flex-direction: column;
  flex: 1;
}
.grid-columns {
  display: flex;
  gap: 4px;
  justify-content: space-between;
  width: 100%;
}
.column {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}
.cell {
  width: 100%;
  padding-bottom: 100%; /* Keep it square */
  height: 0;
  border-radius: 3px;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.1s;
}
.cell:hover {
  transform: scale(1.3);
  z-index: 10;
  box-shadow: 0 0 6px rgba(0,0,0,0.2);
}
.x-axis {
  display: flex;
  justify-content: space-between;
  width: 100%;
  margin-top: 10px;
}
.x-label {
  flex: 1;
  font-size: 10px;
  color: #909399;
  text-align: center;
  white-space: nowrap;
}
.x-label:nth-child(even) {
  opacity: 0;
}

/* Dialog inner styles */
.log-detail-card {
  margin-bottom: 5px;
}
.log-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.log-event {
  font-weight: bold;
}
.log-image {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  background-color: #f5f7fa;
  border: 1px solid #ebeef5;
}

/* Test Dialog Styles */
.test-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  width: 100%;
}
.test-uploader .el-upload:hover {
  border-color: #409eff;
}
.test-uploader-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: #8c939d;
  background: #fbfdff;
}
.test-uploader-icon {
  font-size: 28px;
  margin-bottom: 10px;
}
.test-preview-img {
  width: 100%;
  height: 200px;
  object-fit: contain;
  display: block;
}
.test-result-section {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 15px;
  min-height: 400px;
  background: #fcfcfc;
}
.result-title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}
.test-result-img {
  width: 100%;
  height: 250px;
  border-radius: 4px;
  margin-bottom: 15px;
  background: #000;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>

<template>
  <el-card class="box-card">
    <template #header>
      <div class="card-header">
        <span>{{ $t('network.title') }}</span>
      </div>
    </template>
    
    <el-form :model="form" label-width="120px" v-loading="loading">
      <el-form-item :label="$t('network.mode')">
        <el-radio-group v-model="form.mode">
          <el-radio label="dhcp">{{ $t('network.dhcp') }}</el-radio>
          <el-radio label="static">{{ $t('network.static') }}</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <div v-if="form.mode === 'static'">
        <el-form-item :label="$t('network.ip')">
          <el-input v-model="form.ip" placeholder="192.168.1.100"></el-input>
        </el-form-item>
        <el-form-item :label="$t('network.netmask')">
          <el-input v-model="form.netmask" placeholder="255.255.255.0"></el-input>
        </el-form-item>
        <el-form-item :label="$t('network.gateway')">
          <el-input v-model="form.gateway" placeholder="192.168.1.1"></el-input>
        </el-form-item>
        <el-form-item :label="$t('network.dns')">
          <el-input v-model="form.dns" placeholder="8.8.8.8, 114.114.114.114"></el-input>
        </el-form-item>
      </div>

      <el-form-item>
        <el-button type="primary" @click="saveNetwork">{{ $t('network.save') }}</el-button>
        <p style="color: #e6a23c; margin-left: 15px; font-size: 12px;">{{ $t('network.saveTip') }}</p>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'

const { t } = useI18n()
const loading = ref(false)
const form = ref({
  mode: 'dhcp',
  ip: '',
  netmask: '',
  gateway: '',
  dns: ''
})

const fetchNetwork = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/network')
    form.value = res.data
  } catch (e) {
    ElMessage.error(t('network.fetchFailed'))
  }
  loading.value = false
}

const saveNetwork = () => {
  ElMessageBox.confirm(
    t('network.confirmSave'),
    t('network.confirmTitle'),
    { confirmButtonText: t('network.confirmButton'), cancelButtonText: t('network.cancelButton'), type: 'warning' }
  ).then(async () => {
    loading.value = true
    try {
      await axios.post('/api/network', form.value)
      ElMessage.success(t('network.saveSuccess'))
    } catch (e) {
      ElMessage.error(t('network.saveFailed'))
    }
    loading.value = false
  }).catch(() => {})
}

onMounted(() => {
  fetchNetwork()
})
</script>

<template>
  <div class="camera-grid">
    <div v-for="(camera, index) in cameras" :key="camera.name" class="camera-item">
      <div class="camera-title">{{ camera.name }}</div>
      <div class="camera-view">
        <div :id="`cam-player-${index}`" class="jessibuca-container"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const props = defineProps({
  cameras: {
    type: Array,
    default: () => []
  }
})

// ZLMediaKit 服务器 IP (可以从当前浏览器URL获取，更灵活)
const ZLM_SERVER_IP = window.location.hostname
const players = ref({})

const createPlayer = (containerId, streamName) => {
  const container = document.getElementById(containerId)
  if (!container) return null

  if (!window.Jessibuca) {
    console.error('Jessibuca is not loaded. Please ensure jessibuca.js is in index.html')
    return null
  }

  const player = new window.Jessibuca({
    container: container,
    videoBuffer: 0.2,             // 稍微增加缓冲，防网络抖动
    isResize: true,               // 适应容器大小
    useWASM: true,                // 支持 H.265 解码
    useMSE: true,                 // 优先使用 MSE 硬件解码
    autoWasm: true,
    decoder: '/js/decoder.js',    // 显式指定你的本地 decoder 路径
    hasAudio: false,              // 监控通常不需要声音，关闭可提升性能
    loadingText: t('monitor.loadingText'),
    background: '#000000',
    controlAutoHide: true,
    isNotMute: false,             // 确保静音
    timeout: 10,                  // 设置超时时间(秒)
    heartTimeout: 10,             // 心跳超时
    supportDblclickFullscreen: true, // 双击全屏
    wcsUseVideoRender: true       // 尝试使用 WebCodecs 渲染减轻 WebGL 压力
  })

  // 拼接 ZLM 后端转换好的 FLV 播放地址 
  // 【重要修复】为了突破浏览器对同一域名 HTTP/1.1 最大 6 个并发连接的限制，
  // 我们将 HTTP-FLV 替换为 WS-FLV (WebSocket)，因为 WebSocket 连接数限制要宽容得多。
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const flvUrl = `${wsProtocol}//${ZLM_SERVER_IP}:10081/live/${streamName}.live.flv`
  
  // 监听错误事件进行自动重连
  player.on('error', (error) => {
    console.warn(`[Jessibuca] 播放器 ${streamName} 发生错误:`, error)
    // 延迟 3 秒后尝试重新连接
    setTimeout(() => {
      console.log(`[Jessibuca] 正在尝试重新连接 ${streamName}...`)
      if (player) {
        player.play(flvUrl)
      }
    }, 3000)
  })

  // 监听超时事件进行自动重连
  player.on('timeout', () => {
    console.warn(`[Jessibuca] 播放器 ${streamName} 连接超时`)
    setTimeout(() => {
      console.log(`[Jessibuca] 正在尝试重新连接 ${streamName}...`)
      if (player) {
        player.play(flvUrl)
      }
    }, 3000)
  })
  
  // 定期清理内存机制：每隔 4 小时重新初始化一次播放器
  // 这对 H.265 WASM 软解尤其重要，因为长时间运行容易产生内存碎片
  const reloadInterval = setInterval(() => {
    console.log(`[Jessibuca] 执行定时刷新，清理 ${streamName} 内存...`)
    if (player) {
      player.destroy()
      setTimeout(() => {
        // 重建 DOM 并重新播放
        const newPlayer = createPlayer(containerId, streamName)
        if (newPlayer) {
          // 替换掉引用，保证 onBeforeUnmount 销毁的是新的实例
          // （在 setup 中需要一种机制更新，这里依赖上层引用，由于 reloadInterval 在这里，我们需要巧妙处理）
        }
      }, 1000)
    }
  }, 4 * 60 * 60 * 1000) // 4小时
  
  // 保存定时器 ID，以便销毁时清除
  player._reloadInterval = reloadInterval

  // 开始播放
  player.play(flvUrl)
  return player
}

onMounted(() => {
  // 给一点点延迟，确保 DOM 已经完全渲染完毕再挂载播放器
  setTimeout(() => {
    props.cameras.forEach((camera, index) => {
      // 使用传入的 camera.name 作为 streamName
      const streamName = camera.name
      // 错峰初始化播放器，防止瞬间拉起太多 WebGL 上下文导致浏览器崩溃或卡死
      setTimeout(() => {
        players.value[index] = createPlayer(`cam-player-${index}`, streamName)
      }, index * 300) // 每个播放器延迟 300ms 启动
    })
  }, 500)
})

onBeforeUnmount(() => {
  // 【极其重要】组件销毁时，必须销毁播放器释放内存！
  Object.values(players.value).forEach(player => {
    if (player) {
      if (player._reloadInterval) {
        clearInterval(player._reloadInterval)
      }
      player.destroy()
    }
  })
})
</script>

<script>
export default {
  name: 'CameraGrid'
}
</script>

<style scoped>
.camera-grid {
  display: grid;
  /* 调整为 4 宫格布局：两列，行数自动 */
  grid-template-columns: repeat(2, 1fr);
  grid-auto-rows: minmax(200px, 1fr); /* 保证最小高度，避免太扁 */
  gap: 10px;
  height: 100%;
  overflow-y: auto; /* 流多的时候允许滚动 */
  padding-right: 5px;
}

.camera-item {
  background: #000;
  border: 1px solid #333;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  /* 保持 16:9 的视频比例 */
  aspect-ratio: 16 / 9;
}

.camera-title {
  position: absolute;
  top: 5px;
  left: 10px;
  color: white;
  background-color: rgba(0, 0, 0, 0.5);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 10;
  pointer-events: none;
}

.camera-view {
  flex: 1;
  overflow: hidden;
  position: relative;
  background-color: #000;
}

.jessibuca-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}

/* 自定义滚动条样式 */
.camera-grid::-webkit-scrollbar {
  width: 6px;
}
.camera-grid::-webkit-scrollbar-thumb {
  background-color: #909399;
  border-radius: 3px;
}
.camera-grid::-webkit-scrollbar-track {
  background-color: #f0f2f5;
}
</style>

```

