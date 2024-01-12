// UploadPage.jsx

import { useRouter } from 'next/navigation';
import { useState } from 'react';

import { uploadImage } from '@/api/apis';
import ScaleLoaderComponent from '@/components/loading/ScaleLoader';

const FileSelector = (props: any) => {
    const router = useRouter();
    const [uploading, setUploading] = useState(false);
    
    const uploaded = (event: React.ChangeEvent<HTMLInputElement>) => {
        const fileInput = event.target;
        if (!fileInput.files || fileInput.files.length === 0) {
          return;
        }
      
        const file = fileInput.files[0];
        console.log(file);

        const uploadImageToServer = async () => {
            try {
                setUploading(true);
                const response = await uploadImage(file); 
                const { status, image_url } = response;
                if (status === "1"){
                    console.log(image_url);
                    sessionStorage.setItem('image_url', image_url);
                    router.push(props.redirectTo);
                }
            } catch (error) {
                console.log(error);
            } finally {
                setUploading(false);
            };
        };
        uploadImageToServer();
    };

    return (
        <div className="w-3/4 mx-auto my-20">
            {uploading && <ScaleLoaderComponent />}
            <label
                className="flex justify-center w-full h-60 px-4 rounded-3xl transition bg-white border-2 border-gray-300 border-dashed appearance-none cursor-pointer hover:border-gray-400 focus:outline-none">
                <span className="flex items-center space-x-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24"
                        stroke="currentColor" strokeWidth="2">
                        <path strokeLinecap="round" strokeLinejoin="round"
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <span className="font-medium text-gray-600">
                        拖拽图片到此处或点击上上传
                    </span>
                </span>
                <input type="file" name="file_upload" className="hidden" accept="image/png, image/jpeg, image/jpg" onChange={uploaded} />
            </label>
        </div>
    )
}

export default FileSelector;
