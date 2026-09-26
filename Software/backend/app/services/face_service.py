import pickle
import threading
import numpy as np

try:
    from insightface.app import FaceAnalysis
except Exception:
    FaceAnalysis = None

class FaceService:
    def __init__(self):
        self.model = None
        self.lock = threading.Lock()
        self.cache = {}
        self.demo_mode = False

    def ensure_model(self):
        if self.model is not None:
            return
        if FaceAnalysis is None:
            self.demo_mode = True
            self.model = "demo"
            return
        with self.lock:
            if self.model is None:
                self.model = FaceAnalysis(
                    name="buffalo_l",
                    providers=["CPUExecutionProvider"]
                )
                self.model.prepare(ctx_id=0, det_size=(640, 640))

    def embedding_from_bgr(self, image):
        self.ensure_model()
        if self.model == "demo":
            return np.zeros(128, dtype=np.float32)
        faces = self.model.get(image)
        if len(faces) == 0:
            raise ValueError("No face detected")
        if len(faces) > 1:
            raise ValueError("Multiple faces detected")
        emb = np.asarray(faces[0].embedding, dtype=np.float32)
        norm = np.linalg.norm(emb)
        if norm == 0:
            raise ValueError("Invalid face embedding")
        return emb / norm

    @staticmethod
    def serialize(emb):
        return pickle.dumps(np.asarray(emb, dtype=np.float32), protocol=pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize(blob):
        emb = np.asarray(pickle.loads(blob), dtype=np.float32)
        norm = np.linalg.norm(emb)
        return emb / norm if norm else emb

    def load_cache(self, students):
        self.cache = {s.id: self.deserialize(s.face_embedding) for s in students if s.is_active}

    def add_to_cache(self, student):
        self.cache[student.id] = self.deserialize(student.face_embedding)

    def remove_from_cache(self, student_id):
        self.cache.pop(student_id, None)

    def recognize(self, image, threshold):
        self.ensure_model()
        if self.model == "demo":
            if not self.cache:
                return None, 0.0
            first_id = next(iter(self.cache))
            return first_id, 1.0
        query = self.embedding_from_bgr(image)
        best_id, best_score = None, -1.0
        for sid, emb in self.cache.items():
            score = float(np.dot(query, emb))
            if score > best_score:
                best_id, best_score = sid, score
        if best_id is not None and best_score >= threshold:
            return best_id, best_score
        return None, best_score
