import axios from 'axios'

axios.defaults.baseURL = ''
axios.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';
//axios.defaults.headers.common['y'] = 'y'

export const HTTP = axios.create({
  mode: 'no-cors',
  headers: {
    'Access-Control-Allow-Origin': '*',
  }
})


// Intercept

HTTP.interceptors.response.use((response) => {
  return response;
},  (error) => {
  console.log(error.response.status)
  console.log(error.response.text)
  return Promise.reject(error.response);
})
