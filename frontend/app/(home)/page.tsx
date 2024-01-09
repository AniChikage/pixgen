import Introdcution from "@/components/home/IntroductionVideo";
import Price from "@/components/home/Price";
import Tools from "@/components/home/Tools";
import FAQ from '@/components/home/FAQ';

function Home() {
    return (
        <div>
            <Introdcution />
            <Tools />
            {/* <Price /> */}
            <FAQ />
        </div>
    )
}

export default Home;