"use client"
import React, { useEffect, useLayoutEffect, useState } from 'react';
import Link from 'next/link'
import Image from 'next/image'
import Logo from '../../public/logo.png'
import Avart from '../../public/avart.png'

import { userProfile } from '@/api/apis';

function Nav () {

    const [loggedIn, setLoggedIn] = useState(false);
    const [username, setUsername] = useState('');

    useEffect(() => {
        const username = localStorage.getItem('username');
        if (username === null) {
            const token = localStorage.getItem('token');
            if (token === null){
                setLoggedIn(false);
                setUsername('');
            } else {
                const fetchData = async () => {
                    try {
                        const response = await userProfile(token); 
                        const { status, username } = response;
                        setUsername(username);
                        setLoggedIn(true);
                        localStorage.setItem('username', username);
                        console.log(status);
                        console.log(username);
                    } catch (error) {
                        console.log(error);
                    };
                };
                fetchData();
            }
        } else {
            setUsername(username);
            setLoggedIn(true);
        };
    }, [loggedIn, username]);

    const logout = async(event: { preventDefault: () => void; }) => {
        event.preventDefault();
        setUsername('');
        setLoggedIn(false);
        localStorage.removeItem('username');
        localStorage.removeItem('token');
    }

    return (
        <header className="fixed flex flex-wrap h-14 sm:justify-start sm:flex-nowrap z-50 w-full bg-white bg-opacity-90 border-b border-gray-200 text-sm py-3 sm:py-0 light:bg-gray-800 light:border-gray-700">
            <nav className="relative max-w-[85rem] w-full mx-auto px-4 sm:flex sm:items-center sm:justify-between sm:px-6 lg:px-8" aria-label="Global">
                <div className="flex items-center justify-between">
                <a className="flex-none text-xl font-semibold text-black" href="/" aria-label="Brand">
                <Image
                    className="mx-auto h-5 w-auto"
                    src={Logo}
                    alt="PIXGEN"
                />
                </a>
                <div className="sm:hidden">
                    <button type="button" className="hs-collapse-toggle w-9 h-9 flex justify-center items-center text-sm font-semibold rounded-lg border border-gray-200 text-gray-800 hover:bg-gray-100 disabled:opacity-50 disabled:pointer-events-none light:text-white light:border-gray-700 light:hover:bg-gray-700 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" data-hs-collapse="#navbar-collapse-with-animation" aria-controls="navbar-collapse-with-animation" aria-label="Toggle navigation">
                    <svg className="hs-collapse-open:hidden flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" x2="21" y1="6" y2="6"/><line x1="3" x2="21" y1="12" y2="12"/><line x1="3" x2="21" y1="18" y2="18"/></svg>
                    <svg className="hs-collapse-open:block hidden flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                    </button>
                </div>
                </div>
                <div id="navbar-collapse-with-animation" className="hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow sm:block">
                <div className="flex flex-col gap-y-4 gap-x-0 mt-5 sm:flex-row sm:items-center sm:gap-y-0 sm:gap-x-7 sm:mt-0 sm:ps-7">
                    <a className="font-medium text-base text-gray-800 hover:text-blue-400 sm:py-6 light:text-gray-400 light:hover:text-gray-500" href="/price">价格</a>

                    <div className="hs-dropdown [--strategy:static] md:[--strategy:absolute] [--adaptive:none] md:[--trigger:hover] py-3 md:py-4">
                        <button type="button" className="flex items-center w-full text-gray-800 hover:text-blue-400 font-medium light:text-gray-400 light:hover:text-blue-500 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600 text-base">
                            工具
                            <svg className="flex-shrink-0 ms-2 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                        </button>

                        <div className="hs-dropdown-menu transition-[opacity,margin] duration-[0.1ms] md:duration-[150ms] hs-dropdown-open:opacity-100 opacity-0 w-2/3 hidden z-10 top-full start-0 min-w-[15rem] bg-white md:shadow-2xl rounded-lg py-2 md:p-4 light:bg-gray-800 light:divide-gray-700 before:absolute before:-top-5 before:start-0 before:w-full before:h-5">
                            <div className="md:grid md:grid-cols-2 lg:grid-cols-2 gap-4">
                            <div className="flex flex-col mx-1 md:mx-0">
                                <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="green" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-900 light:text-gray-200">消除背景</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">一键消除背景，可以填充更换背景图片或者背景颜色</p>
                                </div>
                                </a>

                                <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="green" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="7" height="7" x="14" y="3" rx="1"/><path d="M10 21V8a1 1 0 0 0-1-1H4a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5a1 1 0 0 0-1-1H3"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-800 light:text-gray-200">消除物体</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">快速消除图片中的物体、人物等等</p>
                                </div>
                                </a>

                                <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="green" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m7 11 2-2-2-2"/><path d="M11 13h4"/><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-800 light:text-gray-200">背景模糊</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">模糊图片中人物的背景</p>
                                </div>
                                </a>
                            </div>

                            <div className="flex flex-col mx-1 md:mx-0">
                                <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="green" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-800 light:text-gray-200">高清修复</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">一键修复模糊的图片，提供高清画质</p>
                                </div>
                                </a>

                                <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="green" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-800 light:text-gray-200">一键换脸</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">一键用自定义的人脸替换图片中的人脸</p>
                                </div>
                                </a>

                                {/* <a className="group flex gap-x-5 hover:bg-gray-100 rounded-lg p-4 light:text-gray-200 light:hover:bg-gray-900 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="#">
                                <svg className="flex-shrink-0 w-5 h-5 mt-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="black" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" ><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                                <div className="grow">
                                    <p className="font-medium text-gray-800 light:text-gray-200">Community Forum</p>
                                    <p className="text-sm text-gray-500 group-hover:text-gray-800 light:group-hover:text-gray-200">Learn, share, and connect with other Preline users.</p>
                                </div>
                                </a> */}
                            </div>

                            {/* <div className="flex flex-col pt-4 md:pt-0 mx-1 md:mx-0">
                                <span className="text-sm font-semibold uppercase text-gray-800 light:text-gray-200">Customer stories</span>

                                <a className="group mt-2 p-3 flex gap-x-5 items-center rounded-xl hover:bg-gray-100 light:hover:bg-slate-500/10 light:focus:outline-none light:focus:ring-1 light:focus:ring-slate-600" href="#">
                                <Image className="w-32 h-32 rounded-lg" src="https://images.unsplash.com/photo-1648737967328-690548aec14f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=320&h=320&q=80" width={200} height={200} alt="Image Description" />
                                <div className="grow">
                                    <p className="text-sm text-gray-800 light:text-slate-400">
                                    Preline Projects has proved to be most efficient cloud based project tracking and bug tracking tool.
                                    </p>
                                    <p className="mt-3 inline-flex items-center gap-x-1 text-sm text-blue-600 decoration-2 hover:underline font-medium light:text-blue-400 light:hover:text-blue-500 light:focus:outline-none light:focus:ring-1 light:focus:ring-slate-600">
                                    Learn more
                                    <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                                    </p>
                                </div>
                                </a>
                            </div> */}
                            </div>
                        </div>
                        </div>

                    {
                        loggedIn? 
                        <div className="hs-dropdown inline-flex ml-auto">
                            <button id="hs-dropdown-custom-trigger" type="button" className="hs-dropdown-toggle py-1 ps-1 pe-3 inline-flex items-center gap-x-2 text-sm font-semibold rounded-full bg-transparent text-gray-800  hover:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none light:bg-transparent light:text-white light:hover:bg-gray-800 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600">
                                <Image className="w-8 h-8 rounded-full" width={20} height={20} src={Avart.src} alt="Maria" />
                                <span className="text-gray-600 font-medium truncate max-w-[7.5rem] lgiht:text-gray-400">{username}</span>
                                <svg className="hs-dropdown-open:rotate-180 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                            </button>

                            <div className="hs-dropdown-menu transition-[opacity,margin] duration hs-dropdown-open:opacity-100 opacity-0 hidden min-w-[10rem] bg-white shadow-md rounded-lg p-2 mt-2 light:bg-gray-800 light:border light:border-gray-700" aria-labelledby="hs-dropdown-custom-trigger">
                                <a className="flex items-center gap-x-3.5 py-2 px-3 rounded-lg text-sm text-gray-800 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 light:text-gray-400 light:hover:bg-gray-700 light:hover:text-gray-300 light:focus:bg-gray-700" href="/#">
                                个人资料
                                </a>
                                <a className="flex items-center gap-x-3.5 py-2 px-3 rounded-lg text-sm text-gray-800 hover:bg-gray-100 focus:outline-none focus:bg-gray-100 light:text-gray-400 light:hover:bg-gray-700 light:hover:text-gray-300 light:focus:bg-gray-700" href="/#" onClick={logout}>
                                退出
                                </a>
                            </div>
                        </div>
                        :
                        <div className="flex items-center gap-x-2 sm:ms-auto">
                            <a className="flex items-center gap-x-2 font-medium text-gray-500 hover:text-blue-600 light:text-gray-400 light:hover:text-blue-500" href="/login">
                                <svg className="flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                                登录
                            </a>
                        </div>
                    }
                </div>
                </div>
            </nav>
        </header>
    )
}

export default Nav;