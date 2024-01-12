"use client"
import { useRouter } from 'next/navigation';
import React, { useState, useRef, useEffect } from 'react';

import { getImage, upscaler, checkPro } from '@/api/apis';

import { ArrowLeftIcon, ArrowUturnLeftIcon } from '@heroicons/react/24/outline';

const Editor = () => {
    const router = useRouter();
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const maskCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const drawCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const [token, setToken] = useState<string>("");
    const [drawing, setDrawing] = useState(false);
    const [upscaled, setUpscaled] = useState(false);
    const [image, setImage] = useState<File | null>(null);
    const [lastImage, setLastImage] = useState<File | null>(null);
    const [mask, setMask] = useState<File | null>(null);
    const [lines, setLines] = useState([]);
    const [originalImage, setOriginalImage] = useState<File | null>(null);
    const [lineWidth, setLineWidth] = useState(25); 
    const [lineColor, setLineColor] = useState('#00AA00'); 
    const [lineCap, setLineCap] = useState<'round' | 'butt' | 'square'>('round');
    const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
    const [originalImageWidth, setOriginalImageWidth] = useState(0);
    const [originalImageHeight, setOriginalImageHeight] = useState(0);
    const [isMouseOver, setIsMouseOver] = useState(false);
    const [opacity, setOpacity] = useState(1);
    const [processing, setProcessing] = useState(false);
    const [sliderValue, setSliderValue] = useState(25);
    const [recover, setRecover] = useState(false);
    const [imageUrlArray, setImageUrlArray] = useState<string[]>([]);
    const [imageHighUrlArray, setImageHighUrlArray] = useState<string[]>([]);
    const [imageLowUrlArray, setImageLowUrlArray] = useState<string[]>([]);
    const [latestImageUrl, setLatestImageUrl] = useState<string>("");
    const [latestImageHighUrl, setLatestImageHighUrl] = useState<string>("");
    const [latestImageLowUrl, setLatestImageLowUrl] = useState<string>("");
    const [pro, setPro] = useState(false);

    useEffect(() => {
      const image_url = sessionStorage.getItem('image_url');
      renderCanvas(image_url, image_url);
    }, []);

    useEffect(() => {
      const local_token = localStorage.getItem('token');
      if (local_token) {
        setToken(local_token);
      }
    }, []);

    useEffect(() => {
      if (processing) {
        const interval = setInterval(() => {
          setOpacity((prevOpacity) => (prevOpacity === 1 ? 0.3 : 1));
        }, 400);
        return () => clearInterval(interval);
      } else {
        setOpacity(1);
      }
    }, [processing]);

    useEffect(() => {
      console.log(imageHighUrlArray);
    }, [imageHighUrlArray]);

    useEffect(() => {
      console.log(imageLowUrlArray);
    }, [imageLowUrlArray]);

    useEffect(() => {
      const handleRenderCanvas = () => {
        console.log(recover);
        if (recover && imageHighUrlArray.length > 1) {
          const newImageHighUrlArray = imageHighUrlArray.slice(0, -1);
          const image_url = newImageHighUrlArray[newImageHighUrlArray.length - 1];
          setImageHighUrlArray(newImageHighUrlArray);

          const newImageLowUrlArray = imageLowUrlArray.slice(0, -1);
          const image_low_url = newImageLowUrlArray[newImageLowUrlArray.length - 1];
          setImageLowUrlArray(newImageLowUrlArray);

          renderCanvas(image_url, image_low_url);
        }
      };
      handleRenderCanvas();
    }, [recover, imageHighUrlArray, imageLowUrlArray]);


    useEffect(() => {
      const fetchData = async () => {
        try {
          const token = localStorage.getItem('token');
          if (!token) return;
          const response = await checkPro(token);
          const { status, effective } = response;
          console.log(response);
          if (status === "1") {
            if (effective) {
              setPro(true);
            }
          }
        } catch (error) {
            console.log(error);
        };
      };
      fetchData();
    }, []);

    const renderCanvas = (image_high_url: any, image_low_url?: any) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      setLatestImageHighUrl(image_high_url);
      setLatestImageLowUrl(image_low_url);
      if (!recover) {
        const newImageHighUrlArray = [...imageHighUrlArray, image_high_url];
        setImageHighUrlArray(newImageHighUrlArray);
        if (image_low_url) {
          const newImageLowUrlArray = [...imageLowUrlArray, image_low_url];
          setImageLowUrlArray(newImageLowUrlArray);
        }
      } else {
        setRecover(false);
      }

      if (image_low_url) {
          const loadImage = async () => {
              const blob = await getImage(image_low_url);
              if (!blob) {
                console.error('blob is null');
                return;
              }
              const lastImageFile = new File([blob], 'image.png', { type: 'image/png' });
              setLastImage(lastImageFile);

              const img = new Image();
              if (!blob) {
                console.error("blob is null");
                return;
              }
              img.src = URL.createObjectURL(blob);;
              img.onload = () => {
                  const maxCanvasWidth = window.innerWidth * (2 / 3);
                  const maxCanvasHeight = window.innerHeight * (3 / 4);

                  let newWidth = img.width;
                  let newHeight = img.height;
        
                  setOriginalImageWidth(img.width);
                  setOriginalImageHeight(img.height);

                  if (newWidth > maxCanvasWidth) {
                      newHeight = (maxCanvasWidth / img.width) * img.height;
                      newWidth = maxCanvasWidth;
                  }
      
                  if (newHeight > maxCanvasHeight) {
                      newWidth = (maxCanvasHeight / img.height) * img.width;
                      newHeight = maxCanvasHeight;
                  }

                  setCanvasSize({ width: newWidth, height: newHeight });
                  canvas.width = newWidth;
                  canvas.height = newHeight;

                  ctx.drawImage(img, 0, 0, newWidth, newHeight);

                  setProcessing(false);
              };
          };
          loadImage();
      }
    }

  const backTo = async(event: { preventDefault: () => void; }) => {
    router.push('/upscaler');
  }

  const upscalerImage = async(event: { preventDefault: () => void; }) => {
    const canvas = canvasRef.current;
    if (canvas){
      setProcessing(true);
      console.log("dddd");
      if (lastImage) {
        const response = await upscaler(token, lastImage);
        const { status, image_high_url, image_low_url } = response;
        if (status === "1") {
          renderCanvas(image_high_url, image_low_url);
          setUpscaled(false);
        }
      }
    }
  }

  const goPrice = () => {
    router.push('/price');
  };

  const handleDownloadHighClick = async () => {
    try {
      if (pro) {
        if (!latestImageHighUrl) return;
        await fetch(latestImageHighUrl)
        .then(response => response.blob())
        .then(blob => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          const fileName = latestImageHighUrl.substring(latestImageHighUrl.lastIndexOf('/') + 1);
          a.href = url;
          a.download = fileName;
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        })
        .catch(error => console.error('Error downloading image:', error));
      } else {
        const pro_modal = document.getElementById('pro_modal') as HTMLDialogElement | null;
        if (pro_modal) {
          pro_modal.showModal();
        }
      }
      
    } catch (error) {
      console.error('下载图片时发生错误:', error);
    }
  }

  const handleDownloadLowClick = async () => {
    try {
      if (!latestImageLowUrl) return;
      await fetch(latestImageLowUrl)
      .then(response => response.blob())
      .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const fileName = latestImageLowUrl.substring(latestImageLowUrl.lastIndexOf('/') + 1);
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
      })
      .catch(error => console.error('Error downloading image:', error));
    } catch (error) {
      console.error('下载图片时发生错误:', error);
    }
  }

  return (
    <div className='w-full h-screen flex justify-center items-start' 
        style={{ background: "linear-gradient(to right, #000 1px, transparent 1px), linear-gradient(to bottom, #000 1px, transparent 1px)", backgroundSize: "20px 20px" }}
    >
        <header className="fixed flex items-center flex-wrap h-14 sm:justify-start sm:flex-nowrap z-50 w-full bg-black text-sm py-3 sm:py-0 light:bg-gray-800 ">
            <nav className="relative w-full pr-4 sm:flex sm:items-center sm:justify-between" aria-label="Global">
                <div id="navbar-collapse-with-animation" className="hs-collapse hidden overflow-hidden transition-all duration-300 w-40 grow sm:block">
                <div className="flex justify-start flex-col gap-y-4 gap-x-0 mt-5 sm:flex-row sm:items-center sm:gap-y-0 sm:gap-x-3 sm:mt-0 sm:ps-7">
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border  text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                        onClick={backTo}
                    >
                    <ArrowLeftIcon className='h-5 w-5' />
                    返回
                    </button>
                </div>
                </div>

                <div id="navbar-collapse-with-animation" className="hs-collapse hidden overflow-hidden transition-all duration-300 basis-full grow sm:block">
                <div className="flex justify-end flex-col gap-y-4 gap-x-0 mt-5 sm:flex-row sm:items-center sm:gap-y-0 sm:gap-x-3 sm:mt-0 sm:ps-7">
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-gray-200 text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                      onClick={upscalerImage}
                      disabled={processing || upscaled}
                    >
                    一键放大
                    </button>
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-gray-200 text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                      disabled={processing}
                      onClick={handleDownloadLowClick}
                    >
                    下载低分辨率
                    </button>
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-gray-200 text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                      disabled={processing}
                      onClick={ handleDownloadHighClick}
                    >
                    下载高清图片
                    </button>
                    <dialog id="pro_modal" className="modal">
                      <div className="modal-box">
                        <h3 className="font-bold text-lg">付费功能</h3>
                        <p className="py-4">下载高清图片是付费功能，请查看付费计划</p>
                        <div className="modal-action">
                          <form method="dialog">
                            <button className="btn" >取消</button>
                          </form>
                          <form method="dialog">
                            <button className="btn btn-active btn-primary" onClick={goPrice}>去付费</button>
                          </form>
                        </div>
                      </div>
                    </dialog>
                </div>
                </div>
            </nav>
        </header>

        <div className='w-full h-screen flex justify-center items-center bg-black'
          style={{ background: "radial-gradient(circle, #6F6F6F 1px, transparent 1px)", backgroundSize: "30px 30px" }}
        >
          <div className={`relative transition-opacity duration-200 ease-in-out`} style={{opacity: opacity}}>
              <canvas
                  ref={canvasRef}
                  width={900}
                  height={600}
              />
          </div>
        </div>
      {/* <button onClick={sendToBackend}>Send to Backend</button> */}
    </div>
  );
};

export default Editor;
