
export default function Footer () {
    return (
        <footer
        className="bg-neutral-100 text-center text-neutral-600 light:bg-gray-800 light:text-neutral-200">

        <div className="relative mx-auto py-8 max-w-[82rem] text-center justify-between">
            <div className="grid-1 grid gap-8 md:grid-cols-2 lg:grid-cols-4 text-center">
            <div className="">
                <h6
                className="mb-4 flex items-center justify-start font-semibold uppercase ">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="mr-3 h-4 w-4">
                    <path
                    d="M12.378 1.602a.75.75 0 00-.756 0L3 6.632l9 5.25 9-5.25-8.622-5.03zM21.75 7.93l-9 5.25v9l8.628-5.032a.75.75 0 00.372-.648V7.93zM11.25 22.18v-9l-9-5.25v8.57a.75.75 0 00.372.648l8.628 5.033z" />
                </svg>
                PIXGEN
                </h6>
                <p className="mb-4 flex items-center justify-center md:justify-start text-sm">
                AI图片处理
                </p>
            </div>
            <div className="">
                <h6
                className="mb-4 flex justify-start font-semibold uppercase ">
                其他产品
                </h6>
                <p className="mb-4">
                <a href="#!" className="mb-4 flex items-center justify-center md:justify-start text-sm">
                    视频换脸（ 即将推出 ）
                </a>
                </p>
                <p className="mb-4">
                <a href="#!" className="mb-4 flex items-center justify-center md:justify-start text-sm" >
                    智能换声（ 即将推出 ）
                </a>
                </p>
            </div>
            <div className="">
                <h6
                className="mb-4 flex justify-start font-semibold uppercase">
                链接
                </h6>
                <p className="mb-4">
                <a href="#!" className="mb-4 flex items-center justify-center md:justify-start text-sm" >
                    隐私
                </a>
                </p>
                <p className="mb-4">
                <a href="#!" className="mb-4 flex items-center justify-center md:justify-start text-sm" >
                    退款
                </a>
                </p>
            </div>
            <div  className="">
                <h6
                className="mb-4 flex justify-start font-semibold uppercase">
                联系我们
                </h6>
                <p className="mb-4 flex items-center justify-center md:justify-start text-sm">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="mr-3 h-5 w-5">
                    <path
                    d="M11.47 3.84a.75.75 0 011.06 0l8.69 8.69a.75.75 0 101.06-1.06l-8.689-8.69a2.25 2.25 0 00-3.182 0l-8.69 8.69a.75.75 0 001.061 1.06l8.69-8.69z" />
                    <path
                    d="M12 5.432l8.159 8.159c.03.03.06.058.091.086v6.198c0 1.035-.84 1.875-1.875 1.875H15a.75.75 0 01-.75-.75v-4.5a.75.75 0 00-.75-.75h-3a.75.75 0 00-.75.75V21a.75.75 0 01-.75.75H5.625a1.875 1.875 0 01-1.875-1.875v-6.198a2.29 2.29 0 00.091-.086L12 5.43z" />
                </svg>
                北京市海淀区中关村软件园
                </p>
                <p className="mb-4 flex items-center justify-center md:justify-start text-sm">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    className="mr-3 h-5 w-5">
                    <path
                    d="M1.5 8.67v8.58a3 3 0 003 3h15a3 3 0 003-3V8.67l-8.928 5.493a3 3 0 01-3.144 0L1.5 8.67z" />
                    <path
                    d="M22.5 6.908V6.75a3 3 0 00-3-3h-15a3 3 0 00-3 3v.158l9.714 5.978a1.5 1.5 0 001.572 0L22.5 6.908z" />
                </svg>
                pixgen@163.com
                </p>
            </div>
            </div>
        </div>

        <div className="bg-neutral-200 p-3 text-center h-12 light:bg-gray-900">
            {/* <span>© 2023 Copyright:</span> */}
            <a className="h-10 text-neutral-600 light:text-neutral-400 text-xs"  >
                ©2024 PIXGEN. All Rights Reserved. 备案号: 京ICP备2023012598号
            </a>
        </div>
        </footer>
    )
}