"use client"
import Image from 'next/image'
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

import { sendValidationCode, registerUser } from '@/api/apis';
import LoginBG from '@/public/login_bg.jpg';

export default function Register() {

    const router = useRouter();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [repeated, setRepeated] = useState('');
    const [username, setUsername] = useState('');
    const [validation, setValidation] = useState('');
    const [isValidEmail, setIsValidEmail] = useState(true);
    const [isValidPassword, setIsValidPassword] = useState(true);
    const [isValidUsername, setIsValidUsername] = useState(true);
    const [isValidRepeated, setIsValidRepeated] = useState(true);
    const [isValidValidation, setIsValidValidation] = useState(true);
    const [sendValidation, setSendValidation] = useState(0);
    const [showHint, setShowHint] = useState(false);

    const handleEmailChange = (event: { target: { value: any; }; }) => {
        const newEmail = event.target.value;
        setEmail(newEmail);
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        setIsValidEmail(emailRegex.test(newEmail));
    };

    const handleUsernameChange = (event: { target: { value: any; }; }) => {
        const newUsername = event.target.value;
        setUsername(newUsername);
        const usernameRegex = /^.{4,}$/;
        setIsValidUsername(usernameRegex.test(newUsername));
    };

    const handlePasswordChange = (event: { target: { value: any; }; }) => {
        const password = event.target.value;
        setPassword(password);
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%-_*?&]{8,}$/;
        setIsValidPassword(passwordRegex.test(password));
    };

    const handleRepeatedChange = (event: { target: { value: any; }; }) => {
        const newPepeated = event.target.value;
        setRepeated(newPepeated);
        setIsValidRepeated(newPepeated === password);
    };

    const handleValidationChange = (event: { target: { value: any; }; }) => {
        const newValidationCode = event.target.value;
        setValidation(newValidationCode);
    };

    const getValidationCode = async(event: { preventDefault: () => void; }) => {
        if ( email && password && repeated){
            try {
              const response = await sendValidationCode(email); 
              const { status, msg } = response;
              console.log(status);
              console.log(msg);
              if (status == "1"){
                  setSendValidation(1);
              } else {
                  setSendValidation(-1);
              }
            } catch (error) {
              console.log(error);
            };
          }
          else {
              console.log("email or password is empty");
              setIsValidEmail(false);
        }
    }

    const goRegister = async(event: { preventDefault: () => void; }) => {
        if ( email && password && repeated && validation){
            try {
              const response = await registerUser(email, username, password, validation); 
              const { status, msg, token } = response;
              console.log(status);
              console.log(msg);
              if (status == "1") {
                localStorage.setItem("token", token);
                router.push("/");
              }
              else if (status == "-1") {
                setSendValidation(-1);
              } 
              else if (status == "-2") {
                setSendValidation(-2);
              } 
              else if (status == "-3") {
                setSendValidation(-3);
              } 
            } catch (error) {
              console.log(error);
            };
        }
        else {
            console.log("email or password is empty");
            setIsValidEmail(false);
        }
    }

    const goLogin = async(event: { preventDefault: () => void; }) => {
        event.preventDefault();
        router.push("/login");
    }


    return (
        <section className="border-red-500 bg-slate-50 min-h-screen flex items-center justify-center" >
            <div className="bg-gray-100 bg-opacity-5 w-128 p-5 flex rounded-2xl shadow-lg max-w-3xl">
            <div className="md:w-full px-5">
                <h2 className="text-2xl font-bold text-[#002D74] text-center">注册</h2>
                <p className="text-sm mt-4 text-[#002D74]"></p>
                <form className="mt-6" action="#" method="POST">
                <div>
                    {/* <label className="block text-gray-700">邮箱</label> */}
                    { !isValidEmail && <label className="block text-gray-700">请输入有效的邮箱</label> }
                    { sendValidation == -1 && <label className="block text-gray-700">邮箱已注册</label> }
                    <input type="email" name="email" id="email" value={email} onChange={handleEmailChange} placeholder="邮箱地址" className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500 focus:bg-white focus:outline-none text-slate-800" autoFocus required />
                </div>

                <div className="mt-4">
                    {/* <label className="block text-gray-700">用户名</label> */}
                    { !isValidUsername && <label className="block text-gray-700">用户名应不少于4个字符</label> }
                    <input type="username" name="username" id="username" value={username} onChange={handleUsernameChange} placeholder="用户名" className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500 focus:bg-white focus:outline-none text-slate-800" autoFocus required />
                </div>
        
                <div className="mt-4">
                    {
                        // !showHint? <label className="block text-gray-700">密码</label>
                        // : <label className="block text-red-600">密码错误</label>
                    }
                     { !isValidPassword && <label className="block text-gray-700">密码应为不少于8位的字母和数字组合</label> }
                    <input type="password" name="password" id="password" value={password} onChange={handlePasswordChange} placeholder="密码"  className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500
                        focus:bg-white focus:outline-none text-slate-800"  required  />
                </div>

                <div className="mt-4">
                    { !isValidRepeated && <label className="block text-gray-700">密码不匹配</label> }
                    <input type="password" name="repeated" id="repeated" value={repeated} onChange={handleRepeatedChange} placeholder="重复密码"  className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500
                        focus:bg-white focus:outline-none text-slate-800"  required  />
                </div>

                <div className="flex items-center mt-4">
                    {/* <label className="block text-gray-700">邮箱验证码</label> */}
                    {/* { sendValidation === 1 && <label className="block text-gray-700">发送验证码成功</label> }
                    { sendValidation === -1 && <label className="block text-gray-700">发送验证码失败</label> } */}
                    { sendValidation == -2 && <label className="block text-gray-700">验证码过期</label> }
                    { sendValidation == -3 && <label className="block text-gray-700">验证码不正确</label> }
                    <input type="validation" name="validation" id="validation" value={validation} onChange={handleValidationChange} placeholder="邮箱验证码" className="flex-grow px-4 py-3 rounded-lg bg-gray-200 border focus:border-blue-500 focus:bg-white focus:outline-none text-slate-800" required/>
                    <button type="button" className="px-3 py-3 w-36 ml-3 bg-white border rounded-xl duration-300 border-blue-400 hover:bg-blue-400 hover:text-white text-slate-800 " onClick={getValidationCode}>
                        {
                            sendValidation == 0?
                            "发送验证码" : "重新发送验证码"
                        }
                    </button>
                </div>

                <button type="button" className="w-full block bg-blue-500 hover:bg-blue-400 focus:bg-blue-400 text-white font-semibold rounded-lg
                        px-4 py-3 mt-6"
                    onClick={goRegister}
                >
                        注册
                </button>
                </form>

                <div className="text-sm flex justify-between items-center mt-3">
                <p className="text-slate-800"></p>
                <button className="py-2 px-5 ml-3 bg-white border rounded-xl hover:scale-110 duration-300 border-blue-400 text-slate-800 " onClick={goLogin}>登录</button>
                </div>
            </div>

            {/* <div className="w-1/2 md:block hidden ">
                <Image src={LoginBG} width={200} height={400} className="rounded-2xl w-full h-full" alt="page img" />
            </div> */}

            </div>
        </section>
    )
}