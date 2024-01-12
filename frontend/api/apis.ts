
export const API_ENDPOINT = 'https://pixgen.pro:8002'


export async function loginUser(
    email: string,
    password: string
  ) {
    const fd = new FormData()
    fd.append('email', email)
    fd.append('password', password)
  
    try {
      const res = await fetch(`${API_ENDPOINT}/api/user/login_user`, {
        method: 'POST',
        body: fd,
        mode: 'cors',
      })
      console.log(res)
      if (res.ok) {
        const data = await res.json();
        return data;
      }
    } catch (error) {
      throw new Error(`login failed: ${error}`)
    }
}

export async function sendValidationCode(
  email: string
) {
  const fd = new FormData()
  fd.append('email', email)

  try {
    const res = await fetch(`${API_ENDPOINT}/api/user/get_validation_code`, {
      method: 'POST',
      body: fd,
      mode: 'cors',
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (error) {
    throw new Error(`login failed: ${error}`)
  }
}

export async function registerUser(
  email: string,
  username: string,
  password: string,
  validation_code: string
) {
  const fd = new FormData()
  fd.append('email', email)
  fd.append('username', username)
  fd.append('password', password)
  fd.append('validation_code', validation_code)

  try {
    const res = await fetch(`${API_ENDPOINT}/api/user/register_user`, {
      method: 'POST',
      body: fd,
      mode: 'cors',
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (error) {
    throw new Error(`login failed: ${error}`)
  }
}


export async function userProfile(
  token: string,
) {
  try {
    const res = await fetch(`${API_ENDPOINT}/api/user/user_profile`, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (error) {
    throw new Error(`login failed: ${error}`)
  }
}


export async function checkPro(
  token: string,
) {
  try {
    const res = await fetch(`${API_ENDPOINT}/api/user/check_pro`, {
      method: 'POST',
      mode: 'cors',
      headers: {
        'Authorization': 'Bearer ' + token
      }
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      return data;
    }
  } catch (error) {
    throw new Error(`login failed: ${error}`)
  }
}


export async function uploadImage(
  originImage: File,
) {
  try {
    const fd = new FormData()
    fd.append('image', originImage)

    const res = await fetch(`${API_ENDPOINT}/api/utils/upload_image`, {
      method: 'POST',
      mode: 'cors',
      // headers: {
      //   'Content-Type': 'multipart/form-data',
      // },
      body: fd,
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      return data;
    } else {
      const errMsg = await res.text()
      console.log(errMsg);
    }
  } catch (error) {
    throw new Error(`upload failed: ${error}`)
  }
}


export async function getImage(
  image_url: string,
) {
  try {
    const res = await fetch(image_url, {
      method: 'GET',
      mode: 'cors',
    })
    console.log(res)
    if (res.ok) {
      const blob = await res.blob()
      return blob
    } else {
      const errMsg = await res.text()
      console.log(errMsg);
    }
  } catch (error) {
    throw new Error(`upload failed: ${error}`)
  }
}


export async function erase(
  image: File,
  mask: File
) {
  try {
    const fd = new FormData()
    fd.append('image', image)
    fd.append('mask', mask)

    const res = await fetch(`${API_ENDPOINT}/api/plugin/remove_object`, {
      method: 'POST',
      mode: 'cors',
      // headers: {
      //   'Content-Type': 'multipart/form-data',
      // },
      body: fd,
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      console.log(data)
      return data;
    } else {
      const errMsg = await res.text()
      console.log(errMsg);
    }
  } catch (error) {
    throw new Error(`upload failed: ${error}`)
  }
}


export async function upscaler(
  token: string,
  image: File
) {
  try {
    const fd = new FormData()
    fd.append('image', image)

    const res = await fetch(`${API_ENDPOINT}/api/plugin/upscaler`, {
      method: 'POST',
      mode: 'cors',
      // headers: {
      //   'Content-Type': 'multipart/form-data',
      // },
      headers: {
        'Authorization': 'Bearer ' + token
      },
      body: fd,
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      console.log(data)
      return data;
    } else {
      const errMsg = await res.text()
      console.log(errMsg);
    }
  } catch (error) {
    throw new Error(`upsaler failed: ${error}`)
  }
}

export async function blur(
  token: string,
  image: File
) {
  try {
    const fd = new FormData()
    fd.append('image', image)

    const res = await fetch(`${API_ENDPOINT}/api/plugin/blur_bg`, {
      method: 'POST',
      mode: 'cors',
      // headers: {
      //   'Content-Type': 'multipart/form-data',
      // },
      headers: {
        'Authorization': 'Bearer ' + token
      },
      body: fd,
    })
    console.log(res)
    if (res.ok) {
      const data = await res.json();
      console.log(data)
      return data;
    } else {
      const errMsg = await res.text()
      console.log(errMsg);
    }
  } catch (error) {
    throw new Error(`upsaler failed: ${error}`)
  }
}