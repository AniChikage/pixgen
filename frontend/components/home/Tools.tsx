"use client"
import Image from 'next/image'
import { useEffect, useState } from 'react';
import ReactPlayer from 'react-player';

import BlurImage from '@/public/home/blur.jpg'
import RemoveObject from '@/public/home/remove_object.jpg'
import RemoveBG from '@/public/home/remove_bg.jpg'

export default function Tools() {
    
    const [isClient, setIsClient] = useState(false);
    const [hover, setHover] = useState(false);

    useEffect(() => {
        setIsClient(true);
    }, []);

    const handleMouseEnter = () => {
        setHover(true);
    };
    
    const handleMouseLeave = () => {
        setHover(false);
    };

    return (
        <div className="max-w-[85rem] px-4 py-10 sm:px-6 lg:px-8 lg:py-10 mx-auto"
        >
        <div className="max-w-2xl mx-auto text-center mb-10 lg:mb-14">
            <h2 className="text-2xl font-bold md:text-4xl md:leading-tight light:text-black text-black">工具</h2>
            {/* <p className="mt-1 text-gray-600 light:text-gray-400">See how game-changing companies are making the most of every engagement with Preline.</p> */}
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <a className="group hover:bg-gray-100 rounded-xl p-5 transition-all light:hover:bg-white/[.05]" href="/blur">
            <div className="aspect-w-16 aspect-h-10">
                <Image className="w-full object-cover rounded-xl h-64" src={BlurImage} width={200} height={100} alt="Image Description" />
            </div>
            <h3 className="mt-5 text-xl text-gray-800 light:text-gray-300 light:hover:text-white">
                模糊背景
            </h3>
            <p className="mt-3 inline-flex items-center gap-x-1 text-sm  text-gray-900 light:text-gray-200">
                模糊图片中人物的背景
                <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </p>
            </a>

            <a className="group hover:bg-gray-100 rounded-xl p-5 transition-all light:hover:bg-white/[.05]" href="/erase">
            <div className="aspect-w-16 aspect-h-10">
                <Image className="w-full object-cover rounded-xl h-64" src={RemoveObject} width={200} height={100} alt="Image Description" />
            </div>
            <h3 className="mt-5 text-xl text-gray-800 light:text-gray-300 light:hover:text-white">
                橡皮擦
            </h3>
            <p className="mt-3 inline-flex items-center gap-x-1 text-sm  text-gray-800 light:text-gray-200">
                消除任意物体、人物、水印、文字等
                <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </p>
            </a>

            <a className="group hover:bg-gray-100 rounded-xl p-5 transition-all light:hover:bg-white/[.05]" href="/upscaler">
            <div className="aspect-w-16 aspect-h-10">
                <Image className="w-full object-cover rounded-xl h-64" src="https://images.unsplash.com/photo-1657299171054-e679f630a776?ixlib=rb-4.0.3&ixid=MnwxMjA3fDF8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80" width={200} height={100} alt="Image Description" />
            </div>
            <h3 className="mt-5 text-xl text-gray-800 light:text-gray-300 light:hover:text-white">
                高清修复
            </h3>
            <p className="mt-3 inline-flex items-center gap-x-1 text-sm  text-gray-800 light:text-gray-200">
                扩大、修复模糊图片
                <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </p>
            </a>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <a className="group hover:bg-gray-100 rounded-xl p-5 transition-all light:hover:bg-white/[.05]" href="/#">
            <div className="aspect-w-16 aspect-h-10">
                <Image className="w-full object-cover rounded-xl h-64" src={RemoveBG} width={200} height={100} alt="Image Description" />
            </div>
            <h3 className="mt-5 text-xl text-gray-800 light:text-gray-300 light:hover:text-white">
                消除背景
            </h3>
            <p className="mt-3 inline-flex items-center gap-x-1 text-sm  text-gray-900 light:text-gray-200">
                消除图片中的人物背景
                <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </p>
            </a>

            {/* <a className="group hover:bg-gray-100 rounded-xl p-5 transition-all light:hover:bg-white/[.05]" href="/#">
            <div className="aspect-w-16 aspect-h-10 rounded-xl"
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
            >
                {
                    isClient?
                        <ReactPlayer 
                        className="rounded-xl overflow-hidden"
                        url="http://pixgen.pro:8010/images/eraser.mp4"
                        playing={hover} 
                        loop={true} 
                        controls={false}
                        width='100%'
                        height='100%'
                    />
                    : null
                } 
            </div>
            <h3 className="mt-5 text-xl text-gray-800 light:text-gray-300 light:hover:text-white">
                消除背景
            </h3>
            <p className="mt-3 inline-flex items-center gap-x-1 text-sm  text-gray-900 light:text-gray-200">
                消除图片中的人物背景
                <svg className="flex-shrink-0 w-4 h-4 transition ease-in-out group-hover:translate-x-1" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </p>
            </a> */}

        </div>

        </div>
    )
}