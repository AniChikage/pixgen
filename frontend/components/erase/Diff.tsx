import Image from 'next/image';

import DiffIcon from '@/public/home/erase/erase_diff.png'
import DiffdIcon from '@/public/home/erase/erase_diff_removed.png'

function Diff () {
    return (
        <div className="diff aspect-[16/9] w-2/3">
            <div className="diff-item-1">
                <Image alt="daisy" src={DiffIcon} width={400} height={300} />
            </div>
            <div className="diff-item-2">
                <Image alt="daisy" src={DiffdIcon} width={400} height={300} />
            </div>
            <div className="diff-resizer"></div>
        </div>
    )
};

export default Diff;