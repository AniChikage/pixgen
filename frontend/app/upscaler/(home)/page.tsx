"use client"

import Introdcution from "@/components/home/IntroductionUpscaler";
import FileSelector from "@/components/fileSelect/FileSelect";
import Diff from '@/components/erase/Diff';

function Erase() {

    return (
        <div>
            <Introdcution />
            <FileSelector {...{redirectTo: "/upscaler/editor"}} />
            {/* <Diff /> */}
        </div>
    )
}

export default Erase;