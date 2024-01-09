"use client"
import { useRouter } from 'next/navigation';
import { ClipLoader } from 'react-spinners';
import React, { useState, useRef, useEffect } from 'react';

import { getImage, erase, checkPro } from '@/api/apis';

import LoadingSpinner from '@/components/fileSelect/LoadingSpinner';
import ClipLoaderComponent from '@/components/loading/ClipLoader';
import { ArrowLeftIcon, ArrowUturnLeftIcon } from '@heroicons/react/24/outline';
// import './EditorErase.css'
// import './Cursor.css';

// import BackIcon from '@/public/editor/back.svg';

const Editor = () => {
    const router = useRouter();
    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    const maskCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const drawCanvasRef = useRef<HTMLCanvasElement | null>(null);
    const [drawing, setDrawing] = useState(false);
    const [drawed, setDrawed] = useState(false);
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
    const [imageUrlArray, setImageUrlArray] = useState([]);
    const [imageHighUrlArray, setImageHighUrlArray] = useState([]);
    const [imageLowUrlArray, setImageLowUrlArray] = useState([]);
    const [latestImageUrl, setLatestImageUrl] = useState(null);
    const [latestImageHighUrl, setLatestImageHighUrl] = useState(null);
    const [latestImageLowUrl, setLatestImageLowUrl] = useState(null);
    const [pro, setPro] = useState(false);

    useEffect(() => {
      const image_url = sessionStorage.getItem('image_url');
      renderCanvas(image_url, image_url);
    }, []);

    useEffect(() => {
      if (processing) {
        const interval = setInterval(() => {
          setOpacity((prevOpacity) => (prevOpacity === 1 ? 0.3 : 1));
        }, 500);
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
    }, [recover]);


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


    const handleMouseEnter = () => {
      setIsMouseOver(true);
    };

    const handleMouseLeave = (e) => {
      setIsMouseOver(false);
      const drawCanvas = drawCanvasRef.current;
      if (!drawCanvas) return;
      const ctx = drawCanvas.getContext('2d');
      const { offsetX, offsetY } = e.nativeEvent;
  
      if (!ctx) return;
      ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height); 
      ctx.stroke();
    };

    const handleMouseMove = (event: any) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      if (isMouseOver) {
        const { offsetX, offsetY } = event.nativeEvent;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.arc(offsetX, offsetY, 20, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
        ctx.fill();
        ctx.stroke();
      }
    };

    const renderCanvas = (image_url: any, image_low_url?: any) => {
      const canvas = canvasRef.current;
      const maskCanvas = maskCanvasRef.current;
      const drawCanvas = drawCanvasRef.current;
      if (!canvas || !drawCanvas || !maskCanvas) return;

      const ctx = canvas.getContext('2d');
      const maskCtx = drawCanvas.getContext('2d');
      const drawCtx = drawCanvas.getContext('2d');

      if (!ctx) return;

      canvas.addEventListener('mouseenter', handleMouseEnter);
      canvas.addEventListener('mouseleave', handleMouseLeave);
      maskCanvas.addEventListener('mouseenter', handleMouseEnter);
      maskCanvas.addEventListener('mouseleave', handleMouseLeave);
      drawCanvas.addEventListener('mouseenter', handleMouseEnter);
      drawCanvas.addEventListener('mouseleave', handleMouseLeave);

      // setLatestImageUrl(image_url);
      setLatestImageHighUrl(image_url);
      setLatestImageLowUrl(image_low_url);
      if (!recover) {
        // const newImageUrlArray = [...imageUrlArray, image_url];
        // setImageUrlArray(newImageUrlArray);

        const newImageHighUrlArray = [...imageHighUrlArray, image_url];
        setImageHighUrlArray(newImageHighUrlArray);
        if (image_low_url) {
          const newImageLowUrlArray = [...imageLowUrlArray, image_low_url];
          setImageLowUrlArray(newImageLowUrlArray);
        }
      } else {
        setRecover(false);
      }
      // console.log(imageUrlArray);

      if (image_url && ctx && drawCtx && maskCtx) {
          const loadImage = async () => {
              const blob = await getImage(image_url);
              const lastImageFile = new File([blob], 'image.png', { type: 'image/png' });
              setLastImage(lastImageFile);

              const img = new Image();
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
                  maskCanvas.width = newWidth;
                  maskCanvas.height = newHeight;
                  drawCanvas.width = newWidth;
                  drawCanvas.height = newHeight;

                  ctx.drawImage(img, 0, 0, newWidth, newHeight);

                  setProcessing(false);
              };
          };
          loadImage();
      }
      canvas.removeEventListener('mouseenter', handleMouseEnter);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
      maskCanvas.removeEventListener('mouseenter', handleMouseEnter);
      maskCanvas.removeEventListener('mouseleave', handleMouseLeave);
      drawCanvas.removeEventListener('mouseenter', handleMouseEnter);
      drawCanvas.removeEventListener('mouseleave', handleMouseLeave);
    }

    const startDrawing = (e) => {
        const drawCanvas = drawCanvasRef.current;
        if (!drawCanvas) return;
        const ctx = drawCanvas.getContext('2d');
        const { offsetX, offsetY } = e.nativeEvent;
        
        if (!ctx) return;
        ctx.beginPath();
        ctx.moveTo(offsetX, offsetY);
        setDrawing(true);
        setDrawed(true);
    };

  const draw = (e) => {
    if (drawing) {
      const drawCanvas = drawCanvasRef.current;
      if (!drawCanvas) return;
      const ctx = drawCanvas.getContext('2d');
      const { offsetX, offsetY } = e.nativeEvent;
  
      if (!ctx) return;
      ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height); // 清除画布
      ctx.lineTo(offsetX, offsetY);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = sliderValue;
      ctx.lineCap = lineCap; 
      ctx.lineJoin = 'round'
      ctx.globalAlpha = 0.6;
      ctx.globalCompositeOperation = 'source-over';
      ctx.stroke();
    }
    
    if (!drawing) {
      const drawCanvas = drawCanvasRef.current;
      if (!drawCanvas) return;
      const ctx = drawCanvas.getContext('2d');
      const { offsetX, offsetY } = e.nativeEvent;
  
      if (!ctx) return;
      ctx.clearRect(0, 0, drawCanvas.width, drawCanvas.height); // 清除画布
      ctx.beginPath();
      ctx.moveTo(offsetX, offsetY);
      ctx.lineTo(offsetX, offsetY);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';
      ctx.strokeStyle = lineColor;
      ctx.lineWidth = sliderValue;
      ctx.lineCap = lineCap; 
      ctx.lineJoin = 'round'
      ctx.globalAlpha = 0.6;
      ctx.globalCompositeOperation = 'source-over';
      ctx.stroke();
    }
  };

  const endDrawing = () => {
    const drawCanvas = drawCanvasRef.current;
    const maskCanvas = maskCanvasRef.current;
    if (!maskCanvas || !drawCanvas) return;
    
    const maskCtx = maskCanvas.getContext('2d');
    
    if (!maskCtx) return;
    maskCtx.globalAlpha = 1;
    maskCtx.globalCompositeOperation = 'source-over';

    if (drawing){
      maskCtx.drawImage(drawCanvas, 0, 0, maskCanvas.width, maskCanvas.height);
    }

    const drawCtx = drawCanvas.getContext('2d');
    if (!drawCtx) return;
    drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
    setDrawing(false);
    setLines([...lines, drawCanvasRef.current.toDataURL()]);
  };

  const dataURLtoBlob = (dataURL) => {
    const byteString = atob(dataURL.split(',')[1]);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uint8Array = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
      uint8Array[i] = byteString.charCodeAt(i);
    }

    return new Blob([uint8Array], { type: 'image/png' });
  };

  const getMaskFile = () => {
    const maskCanvas = maskCanvasRef.current;
    if (!maskCanvas) return;
    const dataURL = maskCanvas.toDataURL('image/png');
    const blob = dataURLtoBlob(dataURL);
    const file = new File([blob], 'canvas_image.png', { type: 'image/png' });
    return file;
    
  };

  const backTo = async(event: { preventDefault: () => void; }) => {
    router.push('/erase');
  }

  const renderNew = async(image_high_url: any) => {
    console.log(image_high_url);
  }

  const eraseObject = async(event: { preventDefault: () => void; }) => {
    const canvas = drawCanvasRef.current;
    if (lastImage && lines && canvas){
      setProcessing(true);
      const maskFile =  getMaskFile();
      const response = await erase(lastImage, maskFile);
      const { status, image_high_url, image_low_url } = response;
      if (status === "1") {
        renderCanvas(image_high_url, image_low_url);
        setDrawed(false);
      }
    }
  }

  const handleSliderChange = (event: any) => {
    const value = parseInt(event.target.value, 10);
    setSliderValue(value);
  };

  const revoverLast = () => {
    if (imageHighUrlArray.length > 0) {
      setRecover(true);
    }
  };

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
        document.getElementById('my_modal_1').showModal();
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
    <div className='w-full h-screen flex justify-center items-start bg-black'>
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
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-gray-200 text-gray-500 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                      // disabled={true}
                    >
                    笔刷
                    </button>
                    <input type="range" min="10" max="50" value={sliderValue} onChange={handleSliderChange} className="range w-32 range-xs" />
                    {
                      imageHighUrlArray.length > 1?
                      <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border  text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                        disabled={processing}
                      >
                        <ArrowUturnLeftIcon className='h-5 w-5' onClick={revoverLast} />
                      </button>
                      :
                      <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border  text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                        disabled={processing || imageHighUrlArray.length == 1}
                      >
                        <ArrowUturnLeftIcon className='h-5 w-5' />
                      </button>
                    }
                    <button type="button" className="py-2 px-4 inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-gray-200 text-gray-500 hover:border-blue-600 hover:text-blue-600 disabled:opacity-50 disabled:pointer-events-none dark:border-gray-700 dark:text-gray-400 dark:hover:text-blue-500 dark:hover:border-blue-600 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600"
                      onClick={eraseObject}
                      disabled={processing || !drawed}
                    >
                    一键消除
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
                    <dialog id="my_modal_1" className="modal">
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

        <div className='w-full h-screen flex justify-center items-center bg-black'>
          
          <div style={{ position: 'relative', cursor: 'none' , opacity: opacity, transition: 'opacity 0.5s ease-in-out', }}>
              <canvas
                  ref={canvasRef}
                  width={900}
                  height={600}
                  onMouseDown={startDrawing}
                  onMouseMove={draw}
                  onMouseUp={endDrawing}
                  onMouseOut={endDrawing}
                  onMouseEnter={handleMouseEnter}
                  onMouseLeave={handleMouseLeave}
              />
              <canvas
                  ref={maskCanvasRef}
                  width={900}
                  height={600}
                  style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
              />
              <canvas
                  ref={drawCanvasRef}
                  width={900}
                  height={600}
                  style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
              />
          </div>
        </div>
      {/* <button onClick={sendToBackend}>Send to Backend</button> */}
    </div>
  );
};

export default Editor;
