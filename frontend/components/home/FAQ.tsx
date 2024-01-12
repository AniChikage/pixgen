
function FAQ () {
    return (
        <div className="max-w-[85rem] px-4 py-10 sm:px-6 lg:px-8 lg:py-14 mx-auto">
        <div className="max-w-2xl mx-auto text-center mb-10 lg:mb-14">
            <h2 className="text-2xl font-bold md:text-3xl md:leading-tight text-gray-800 light:text-gray-200">
            常见问题
            </h2>
        </div>

        <div className="max-w-7xl mx-auto">
            <div className="grid sm:grid-cols-3 gap-6 md:gap-12">

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                我不想付费，能不能使用？
                </h3>
                <p className="mt-2 text-gray-600 light:text-gray-400">
                可以！我们提供免费服务，不过由于资源问题，我们对免费版的一些功能做了限制，您如果想有更好的体验，可以选择适合您的付费计划
                </p>
            </div>

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                付费都有什么高阶功能？
                </h3>
                <p className="t mt-2 text-gray-600 light:text-gray-400">
                付费用户可以使用更好的模型，速度和效果都比免费的好
                </p>
            </div>

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                我就今天用一下，不想长期付费
                </h3>
                <p className="mt-2 text-gray-600 light:text-gray-400">
                可以！我们提供了一天的付费计划，比如您可能只需要今天处理几张照片，那您可以选择这个计划， 一天之内您可以使用所有付费功能
                </p>
            </div>

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                为什么比其他网站便宜？
                </h3>
                <p className="mt-2 text-gray-600 light:text-gray-400">
                这就是我们的优势！我们优化了模型和部署架构，很大程度的降低了成本
                </p>
            </div>

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                我只是偶尔需要用
                </h3>
                <p className="mt-2 text-gray-600 light:text-gray-400">
                那“灵活”付费计划非常适合您，只要还有剩余次数，您可以一直使用，不管任何时间
                </p>
            </div>

            <div className="py-4">
                <h3 className="text-base font-semibold text-gray-800 light:text-gray-200">
                网站会不会保存用户的数据？
                </h3>
                <p className="mt-2 text-gray-600 light:text-gray-400">
                不会保存，即用即删
                </p>
            </div>
            </div>
        </div>
        </div>
    )
};

export default FAQ;