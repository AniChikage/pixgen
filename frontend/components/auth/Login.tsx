"use client"
import React, { useEffect, useState, useContext } from 'react';
// import { Link, useHistory, Redirect } from 'react-router-dom';
import { loginUser } from '@/api/apis';

import Image from 'next/image'
import Logo from '../../public/logo.png'


export default function Login() {

    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [repeated, setRepeated] = useState('');
    const [passwordsMatch, setPasswordsMatch] = useState(true);
    const [isValidPassword, setIsValidPassword] = useState(true);
    const [isAllCompeleted, setIsAllCompeleted] = useState(true);
    const [isValidEmail, setIsValidEmail] = useState(true);
    const [isValidUsername, setIsValidUsername] = useState(true);
    const [isCheckboxChecked, setIsCheckboxChecked] = useState(false);
    const [isSuccess, setIsSuccess] = useState(false);  
    const [isFailed, setIsFailed] = useState(false);  
    const [failedMsg, setFailedMsg] = useState('');
    // const history = useHistory();
    // const delay = (milliseconds) => new Promise(resolve => setTimeout(resolve, milliseconds));


    const handleEmailChange = (event: { target: { value: any; }; }) => {
      const newEmail = event.target.value;
      setEmail(newEmail);
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      setIsValidEmail(emailRegex.test(newEmail));
    };

    // const handleUsernameChange = (event) => {
    //   const username = event.target.value;
    //   setUsername(username);
    //   setIsValidUsername(username.length >= 3);
    // };

    // const handleCheckboxChange = (event) => {
    //   setIsCheckboxChecked(event.target.checked);
    // };

    const handlePasswordChange = (event: { target: { value: any; }; }) => {
      const password = event.target.value;
      setPassword(password);
      const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%-_*?&]{8,}$/;
      setIsValidPassword(passwordRegex.test(password));
    };

    // const handleRepeatedChange = (event) => {
    //   const repeated = event.target.value;
    //   setRepeated(repeated)
    //   setPasswordsMatch(password === repeated);
    // };

    const login = async(event: { preventDefault: () => void; }) => {
      event.preventDefault();
      if ( email && password){
        try {
          const response = await loginUser(email, password); 
          const { status, msg, data } = response;
          console.log(status)
          console.log(msg)
          if (status === "0"){
            setIsSuccess(true);
            setIsFailed(false);
            // await delay(2000);
            setIsSuccess(false);
            const loginStatus = {
              email,
              data,
              loginTime: new Date().toLocaleString(), 
            };
            localStorage.setItem('loginStatus', JSON.stringify(loginStatus));
            // history.push('/');
          } else {
            setIsSuccess(false);
            setFailedMsg(msg);
            setIsFailed(true);
          }
        } catch (error) {
          setIsSuccess(false);
          setFailedMsg("邮箱密码错误");
          setIsFailed(true);
          console.error('Error during API call:', error);
        };
      }
      else {
        setIsSuccess(false);
        setFailedMsg("请检查输入信息")
        setIsFailed(true);
      }
    }

    return (
        <div className="flex h-full flex-1 flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <Image className="mx-auto h-10 w-auto" src={Logo.src} 
            width={500}
            height={300} alt="PIXGEN" />
          <h2 className="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-slate-300	">
            登录PIXGEN账户
          </h2>
        </div>

        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form className="space-y-6" action="#" method="POST">
            <div>
              <label htmlFor="email" className="block text-sm font-medium leading-6 text-slate-300	">
                邮箱
              </label>
              <div className="mt-2">
                <input
                  // id="email"
                  name="email"
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  autoComplete="off"
                  placeholder="邮箱"
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-medium leading-6 text-slate-300	">
                  密码
                </label>
                <div className="text-sm">
                  <a href="#" className="font-semibold text-indigo-600 hover:text-indigo-500">
                    忘记密码？
                  </a>
                </div>
              </div>
              <div className="mt-2">
                <input
                  id="password"
                  name="password"
                  type="password"
                  value={password}
                  onChange={handlePasswordChange}
                  autoComplete="current-password"
                  required
                  className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                />
              </div>
            </div>

            <div>
              <button
                type="submit"
                onClick={login}
                className="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
              >
                登录
              </button>
            </div>
          </form>

          <p className="mt-10 text-center text-sm text-gray-500">
            
            <a href="/" className="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">
              返回主页
            </a>
          </p>
        </div>
      </div>
    )
}