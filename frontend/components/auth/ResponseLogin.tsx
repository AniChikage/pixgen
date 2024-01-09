"use client"
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

import { loginUser } from '@/api/apis';


export default function Login() {

    const router = useRouter();

    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isValidEmail, setIsValidEmail] = useState(true);
    const [isValidPassword, setIsValidPassword] = useState(true);
    const [showHint, setShowHint] = useState(false);

    const handleEmailChange = (event: { target: { value: any; }; }) => {
        const newEmail = event.target.value;
        setEmail(newEmail);
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        setIsValidEmail(emailRegex.test(newEmail));
    };

    const handlePasswordChange = (event: { target: { value: any; }; }) => {
        const password = event.target.value;
        setPassword(password);
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%-_*?&]{8,}$/;
        setIsValidPassword(passwordRegex.test(password));
      };

    const login = async(event: { preventDefault: () => void; }) => {
        event.preventDefault();
        if ( email && password){
          try {
            const response = await loginUser(email, password); 
            const { status, msg, token } = response;
            console.log(status);
            console.log(msg);
            console.log(token);
            if (status === "1"){
                localStorage.setItem("token", token);
                router.push("/");
            } else {
                setShowHint(true);
            }
          } catch (error) {
            console.log(error);
            setShowHint(true);
          };
        }
        else {
            console.log("email or password is empty");
        }
    }


    return (
        <section className="border-red-500 bg-gray-900 min-h-screen flex items-center justify-center">
            <div className="bg-gray-100 p-5 flex rounded-2xl shadow-lg max-w-3xl">
            <div className="md:w-1/2 px-5">
                <h2 className="text-2xl font-bold text-[#002D74]">登录</h2>
                <p className="text-sm mt-4 text-[#002D74]"></p>
                <form className="mt-6" action="#" method="POST">
                <div>
                    <label className="block text-gray-700">邮箱</label>
                    <input type="email" name="email" id="email" value={email} onChange={handleEmailChange} placeholder="Enter Email Address" className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500 focus:bg-white focus:outline-none text-slate-800" autoFocus required />
                </div>
        
                <div className="mt-4">
                    {
                        !showHint? <label className="block text-gray-700">密码</label>
                        : <label className="block text-red-600">密码错误</label>
                    }
                    {/* <label className="block text-gray-700">密码</label> */}
                    <input type="password" name="password" id="password" value={password} onChange={handlePasswordChange} placeholder="Enter Password"  className="w-full px-4 py-3 rounded-lg bg-gray-200 mt-2 border focus:border-blue-500
                        focus:bg-white focus:outline-none text-slate-800"  required  />
                </div>

                <div className="text-right mt-2">
                    <a href="#" className="text-sm font-semibold text-gray-700 hover:text-blue-700 focus:text-blue-700">忘记密码？</a>
                </div>
        
                <button type="submit" onClick={login} className="w-full block bg-blue-500 hover:bg-blue-400 focus:bg-blue-400 text-white font-semibold rounded-lg
                        px-4 py-3 mt-6">登录</button>
                </form>

                <div className="mt-7 grid grid-cols-3 items-center text-gray-500">
                <hr className="border-gray-500" />
                <p className="text-center text-sm">或</p>
                <hr className="border-gray-500" />
                </div>

                <button className="bg-white border py-2 w-full rounded-xl mt-5 flex justify-center items-center text-sm hover:scale-105 duration-300 ">
                <svg xmlns="http://www.w3.org/2000/svg"  className="w-6 h-6" viewBox="0 0 48 48"><defs><path id="a" d="M44.5 20H24v8.5h11.8C34.7 33.9 30.1 37 24 37c-7.2 0-13-5.8-13-13s5.8-13 13-13c3.1 0 5.9 1.1 8.1 2.9l6.4-6.4C34.6 4.1 29.6 2 24 2 11.8 2 2 11.8 2 24s9.8 22 22 22c11 0 21-8 21-22 0-1.3-.2-2.7-.5-4z"/></defs><path clipPath="url(#b)" fill="#FBBC05" d="M0 37V11l17 13z"/><path clipPath="url(#b)" fill="#EA4335" d="M0 11l17 13 7-6.1L48 14V0H0z"/><path clipPath="url(#b)" fill="#34A853" d="M0 37l30-23 7.9 1L48 0v48H0z"/><path clipPath="url(#b)" fill="#4285F4" d="M48 48L17 24l-4-3 35-10z"/></svg>
                <span className = "ml-4 text-slate-800">用google登录</span>
                </button>

                <div className="text-sm flex justify-between items-center mt-3">
                <p className="text-slate-800">还没有账号？</p>
                <button className="py-2 px-5 ml-3 bg-white border rounded-xl hover:scale-110 duration-300 border-blue-400 text-slate-800 ">注册</button>
                </div>
            </div>

            <div className="w-1/2 md:block hidden ">
                <img src="https://images.unsplash.com/photo-1614741118887-7a4ee193a5fa?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1887&q=80" className="rounded-2xl" alt="page img" />
            </div>

            </div>
        </section>
    )
}