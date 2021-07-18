import axios from 'axios';

async function gen_category(url) {
  const value = await axios.get(url);
  return value.data;
}

export function get_tabs(url) {
  let data;
  gen_category(url).then(
    (value) => { data = value; },
  );
  return data;
}

export default {
  gen_category,
};
