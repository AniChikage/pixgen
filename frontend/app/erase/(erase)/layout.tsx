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
        <title>Create Next App</title>
        <meta name="description" content="Generated by create next app" />
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
