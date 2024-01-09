"use client";
import React, { useRef, useEffect, useState, useCallback } from 'react';
import {
    ReactZoomPanPinchRef,
    TransformComponent,
    TransformWrapper,
} from 'react-zoom-pan-pinch'

import './EditorErase.scss'
import { getImage } from '@/api/apis';

const Editor = () => {
    const [image, setImage] = useState(null);
    const canvasRef = useRef(null);
    const viewportRef = useRef<ReactZoomPanPinchRef | undefined | null>()
    const [isPanning, setIsPanning] = useState<boolean>(false)
    const [scale, setScale] = useState<number>(1)
    const [panned, setPanned] = useState<boolean>(false)
    const [minScale, setMinScale] = useState<number>(1.0)
    const isProcessing = useState(false)
    const showBrush = useState(false)
    const [sliderPos, setSliderPos] = useState<number>(0)
    const [selectedColor, setSelectedColor] = useState("#FFFFFF");
    const [context, setContext] = useState<CanvasRenderingContext2D>()
    
    const image_url = sessionStorage.getItem('image_url')
    console.log(image_url)


    const getCursor = useCallback(() => {
        if (isPanning) {
          return 'grab'
        }
        if (showBrush) {
          return 'none'
        }
        return undefined
    }, [showBrush, isPanning])


    useEffect(() => {
        const loadImage = async () => {
            try {
                console.log(image_url);
                console.log(canvasRef.current);
                if (image_url && canvasRef.current) {
                    const canvas = canvasRef.current;
                    const ctx = canvas.getContext('2d');
                    const blob = await getImage(image_url);

                    if (ctx) {
                        const img = new Image();
                        img.src = URL.createObjectURL(blob);
                        img.onload = () => {
                            const canvasWidth = canvas.width;
                            const canvasHeight = canvas.height;

                            ctx.clearRect(0, 0, canvasWidth, canvasHeight);
                            ctx.drawImage(img, 0, 0, img.width, img.height);

                        //     const aspectRatio = img.width / img.height;
                        //     const canvasAspectRatio = canvasWidth / canvasHeight;

                        //     if (aspectRatio > canvasAspectRatio) {
                        //         const scaledWidth = canvasWidth;
                        //         const scaledHeight = canvasWidth / aspectRatio;
                        //         const y = (canvasHeight - scaledHeight) / 2;
                        //         ctx.drawImage(img, 0, y, scaledWidth, scaledHeight);
                        //     } else {
                        //         const scaledHeight = canvasHeight;
                        //         const scaledWidth = canvasHeight * aspectRatio;
                        //         const x = (canvasWidth - scaledWidth) / 2;
                        //         ctx.drawImage(img, x, 0, scaledWidth, scaledHeight);
                        //     }
                        };
                    } 
                }   
            } catch (error) {
              console.error('Error loading image:', error);
            }
        };
        loadImage();
    }, [image_url, canvasRef]);

    return (
        <div className="w-full h-screen flex justify-center items-center bg-slate-400 ">
            <canvas className='w-2/3 h-2/3 flex justify-center items-center bg-black' ref={canvasRef}></canvas>
        </div>
    )
}

export default Editor;
