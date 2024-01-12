"use client"
import Head from 'next/head';
import '@/styles/globals.css'

import Nav from '@/components/header/Nav'
import Footer from '@/components/footer/BasicFooter'
import PrelineScript from '@/components/PrelineScript'

import { RecoilRoot } from 'recoil';

export default function RootLayout({ children, }: Readonly<{ children: React.ReactNode }>) {
  return (
    <RecoilRoot>
      <Head>
        <title>PIXGEN</title>
        <meta name="description" content="智能AI图片处理工具, AI赋能" />
        <meta name="keywords" content="一键, 消除物体, 模糊, 消除背景, 换脸, 人物换脸" />
      </Head>

      <html lang="en">
        <body>
          <Nav />
          {children}
          <Footer />
        </body>
        <PrelineScript />
      </html>
    </RecoilRoot>
  )
}
