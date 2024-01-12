"use client"
import { useRouter } from 'next/navigation'
import React, { useEffect, useState } from 'react';
import {
    CursorArrowRaysIcon,
    EyeIcon,
    ArrowsPointingOutIcon,
    ArrowDownTrayIcon,
    PhotoIcon,
    ArrowDownOnSquareIcon,
    ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import Link from 'next/link'
import Image from 'next/image'
import Logo from '../../public/logo.png'
import Avart from '../../public/avart.png'

import { userProfile } from '@/api/apis';

function Nav () {
    const [loggedIn, setLoggedIn] = useState(false);
    const [username, setUsername] = useState('');
    const router = useRouter();

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
            console.log("local");
            setUsername(username);
            setLoggedIn(true);
        };
        // fetchData();
    }, []);

    const logout = async(event: { preventDefault: () => void; }) => {
        event.preventDefault();
        setUsername('');
        setLoggedIn(false);
        localStorage.removeItem('username');
        localStorage.removeItem('token');
    }

    const backTo = async(event: { preventDefault: () => void; }) => {
        router.push('/erase');
    }

    return (
        <header className="fixed flex flex-wrap h-14 sm:justify-start sm:flex-nowrap z-50 w-full bg-black border-b border-gray-900 text-sm py-3 sm:py-0 light:bg-gray-800 light:border-gray-700">
            <nav className="relative max-w-[85rem] w-full mx-auto px-4 sm:flex sm:items-center sm:justify-between sm:px-6 lg:px-8" aria-label="Global">
                <div id="navbar-collapse-with-animation" className="hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow sm:block">
                <div className="flex justify-start flex-col gap-y-4 gap-x-0 mt-5 sm:flex-row sm:items-center sm:gap-y-0 sm:gap-x-3 sm:mt-0 sm:ps-7">
                    <button type="button" className="py-2 px-2 inline-flex items-center gap-x-1 text-sm font-semibold rounded-lg border border-transparent bg-white/10 text-white hover:bg-white/20 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                        onClick={backTo}
                    >
                    返回
                    </button>
                </div>
                </div>
                <div id="navbar-collapse-with-animation" className="hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow sm:block">
                <div className="flex justify-end flex-col gap-y-4 gap-x-0 mt-5 sm:flex-row sm:items-center sm:gap-y-0 sm:gap-x-3 sm:mt-0 sm:ps-7">
                    <button type="button" className="py-2 px-2 inline-flex items-center gap-x-1 text-sm font-semibold rounded-lg border border-transparent bg-white/10 text-white hover:bg-white/20 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">
                    下载低分辨率
                    </button>
                    <button type="button" className="py-2 px-2 inline-flex items-center gap-x-1 text-sm font-semibold rounded-lg border border-transparent bg-white/10 text-white hover:bg-white/20 disabled:opacity-50 disabled:pointer-events-none dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">
                    下载高清图片
                    </button>
                </div>
                </div>
            </nav>
        </header>
    )
}

export default Nav;