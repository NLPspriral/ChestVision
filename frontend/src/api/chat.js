/**
 * 智能体对话相关 API 接口
 */
import request from "@/utils/request";

/**
 * 获取当前用户的会话列表
 * @param {Object} params - { status?, limit?, offset? }
 */
export function getSessionsApi(params = {}) {
  return request.get("/chat/sessions", { params });
}

/**
 * 获取指定会话的消息历史
 * @param {number} sessionId
 * @param {Object} params - { limit?, offset? }
 */
export function getSessionMessagesApi(sessionId, params = {}) {
  return request.get(`/chat/sessions/${sessionId}/messages`, { params });
}

/**
 * 删除指定会话
 * @param {number} sessionId
 */
export function deleteSessionApi(sessionId) {
  return request.delete(`/chat/sessions/${sessionId}`);
}

/**
 * 归档指定会话
 * @param {number} sessionId
 */
export function archiveSessionApi(sessionId) {
  return request.put(`/chat/sessions/${sessionId}/archive`);
}

/**
 * 上传胸片文件
 * @param {File} file
 */
export function uploadImageApi(file) {
  const fd = new FormData();
  fd.append("file", file);
  return request.post("/chat/upload", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}
