import numpy as np
import json
from sklearn.cluster import KMeans

def extract_features(user_data):
    """
    Chuyển đổi dữ liệu Holland & Big Five thành vector 11 chiều (chuẩn hóa 0-1)
    """
    try:
        holland = user_data.get('holland', {})
        big_five = user_data.get('big_five', {})
        
        # Lấy giá trị mặc định là 50 (mức trung bình) nếu thiếu
        r = holland.get('R', 50) / 100.0
        i = holland.get('I', 50) / 100.0
        a = holland.get('A', 50) / 100.0
        s = holland.get('S', 50) / 100.0
        e = holland.get('E', 50) / 100.0
        c = holland.get('C', 50) / 100.0
        
        bf_o = big_five.get('O', 50) / 100.0
        bf_c = big_five.get('C', 50) / 100.0
        bf_e = big_five.get('E', 50) / 100.0
        bf_a = big_five.get('A', 50) / 100.0
        bf_n = big_five.get('N', 50) / 100.0
        
        return [r, i, a, s, e, c, bf_o, bf_c, bf_e, bf_a, bf_n]
    except Exception:
        return [0.5] * 11

def label_cluster(centroid_vector):
    """
    Gắn nhãn nhóm dựa trên centroid (điểm trung tâm của nhóm)
    Holland index: 0-R, 1-I, 2-A, 3-S, 4-E, 5-C
    """
    holland_scores = centroid_vector[:6]
    labels = ['Thực tế', 'Nghiên cứu', 'Nghệ thuật', 'Xã hội', 'Quản lý', 'Nghiệp vụ']
    
    # Lấy 2 đặc điểm cao nhất
    top_2_idx = np.argsort(holland_scores)[-2:][::-1]
    
    # Tính chất Big Five nổi bật (index 6-10)
    bf_scores = centroid_vector[6:]
    bf_labels = ['Sáng tạo', 'Kỷ luật', 'Hướng ngoại', 'Hòa đồng', 'Nhạy cảm']
    top_bf_idx = np.argmax(bf_scores)
    
    if bf_scores[top_bf_idx] > 0.6:
        return f"Nhóm {labels[top_2_idx[0]]} - {labels[top_2_idx[1]]} ({bf_labels[top_bf_idx]})"
    return f"Nhóm {labels[top_2_idx[0]]} & {labels[top_2_idx[1]]}"

def run_clustering(users_data, n_clusters=5):
    """
    Chạy KMeans clustering trên danh sách người dùng.
    users_data là list các dict: {"user_id": id, "profile": parsed_json_content}
    Trả về list chứa thông tin update cho user_clusters.
    """
    if len(users_data) < 2:
        return [] # Quá ít người dùng để clustering
        
    actual_clusters = min(n_clusters, len(users_data) - 1 if len(users_data) > 2 else 2)
    
    user_ids = []
    features = []
    
    for u in users_data:
        user_ids.append(u['user_id'])
        features.append(extract_features(u['profile']))
        
    X = np.array(features)
    
    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    kmeans.fit(X)
    
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    
    # Chuẩn bị dữ liệu trả về để lưu vào DB
    updates = []
    for idx, user_id in enumerate(user_ids):
        cluster_id = int(labels[idx])
        centroid = centroids[cluster_id]
        feature_vector = features[idx]
        
        # Tính similarity score (khoảng cách Euclid, càng nhỏ càng giống)
        distance = float(np.linalg.norm(np.array(feature_vector) - centroid))
        
        cluster_label = label_cluster(centroid)
        
        updates.append({
            "user_id": str(user_id),
            "cluster_id": cluster_id,
            "cluster_label": cluster_label,
            "feature_vector": feature_vector,
            "similarity_score": distance
        })
        
    return updates
