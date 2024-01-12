"use client"

import Introdcution from "@/components/home/IntroductionBlur";
import FileSelector from "@/components/fileSelect/FileSelect";
import Diff from '@/components/erase/Diff';

function Erase() {

    return (
        <div>
            <Introdcution />
            <FileSelector {...{redirectTo: "/blur/editor"}} />
            {/* <Diff /> */}
        </div>
    )
}

export default Erase;