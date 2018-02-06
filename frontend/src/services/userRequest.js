import {request, config} from '../utils';

const {CORS, api} = config



// 新建 request
export function createNewUserRequest(payload) {
  // let category = encodeURIComponent(payload.category)
  // payload.user_ID = localStorage.getItem('user_ID')
  // noinspection JSAnnotator
  return request(`${CORS}/user_request`, {
    method: 'post',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_id:payload.user_ID,
      request_title:payload.requestTitle,
      request_description:payload.requestDescription,
      request_dataset:payload.requestDataset,
    }),
  });
}


// 获取某一个用户下 所有 request
export function fetchUserRequestByUserID(payload) {
  let category = encodeURIComponent(payload.category)
  return request(`${CORS}/user_request?user_ID=${payload.user_ID}&category=${category}&skipping=${payload.skipping}`);
}


// 获取所有的 request
export function fetchAllUserRequest() {
  return request(`${CORS}/user_request`);
}


// 获取一个
export function fetchOneUserRequest(payload) {
  return request(`${CORS}/user_request?user_request_id=${payload.user_request_ID}`);
}


// 关键词搜索
export function searchUserRequest(payload) {
  return request(`${CORS}/user_request?searchStr=${payload.searchStr}`);
}