
export default function Introdcution() {
    return (
        <div className="relative overflow-hidden"
        >
        <div className="max-w-[85rem] mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="max-w-2xl text-center mx-auto mt-10">
                <h1 className="block text-3xl font-bold text-gray-800 sm:text-4xl md:text-5xl light:text-white"><span className="text-blue-600">几秒内</span>创造令人惊叹的视觉效果 </h1>
                {/* <p className="mt-3 text-lg text-gray-800 light:text-gray-400">AI + 快 + 智能</p> */}
            </div>

            <div className="mt-10 relative max-w-5xl mx-auto">
            <div className="w-full object-cover h-96 sm:h-[480px] bg-[url('https://images.unsplash.com/photo-1606868306217-dbf5046868d2?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1981&q=80')] bg-no-repeat bg-center bg-cover rounded-xl"></div>

            <div className="absolute inset-0 w-full h-full">
                <div className="flex flex-col justify-center items-center w-full h-full">
                <a className="py-3 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-full border border-gray-200 bg-white text-gray-800 shadow-sm hover:bg-gray-50 disabled:opacity-50 disabled:pointer-events-none light:bg-slate-900 light:border-gray-700 light:text-white light:hover:bg-gray-800 light:focus:outline-none light:focus:ring-1 light:focus:ring-gray-600" href="/#">
                    <svg className="flex-shrink-0 w-4 h-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    Play the overview
                </a>
                </div>
            </div>

            <div className="absolute bottom-12 -start-20 -z-[1] w-48 h-48 bg-gradient-to-b from-orange-500 to-white p-px rounded-lg light:to-slate-900">
                <div className="bg-white w-48 h-48 rounded-lg light:bg-slate-900"></div>
            </div>

            <div className="absolute -top-12 -end-20 -z-[1] w-48 h-48 bg-gradient-to-t from-blue-600 to-cyan-400 p-px rounded-full">
                <div className="bg-white w-48 h-48 rounded-full light:bg-slate-900"></div>
            </div>
            </div>
        </div>
        </div>
    )
}