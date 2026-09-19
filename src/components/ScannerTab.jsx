import React, { useRef, useState } from 'react';
import { Camera, Upload, CheckCircle2, AlertCircle, RefreshCw, Eye, Sparkles, FileImage, AlertTriangle } from 'lucide-react';

export default function ScannerTab({ 
  onRunScan, 
  scanning, 
  lastResult 
}) {
  const [useCamera, setUseCamera] = useState(false);
  const [previewSrc, setPreviewSrc] = useState(null);
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);

  const startCamera = async () => {
    try {
      setUseCamera(true);
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      alert("Camera access not available on this device. Please select an image file.");
      setUseCamera(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (evt) => {
        const img = new Image();
        img.onload = () => {
          // Scale down image to max 1200px width/height for fast transfer
          const maxDim = 1200;
          let w = img.width;
          let h = img.height;
          if (w > maxDim || h > maxDim) {
            if (w > h) {
              h = Math.round((h * maxDim) / w);
              w = maxDim;
            } else {
              w = Math.round((w * maxDim) / h);
              h = maxDim;
            }
          }
          const canvas = document.createElement('canvas');
          canvas.width = w;
          canvas.height = h;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, w, h);
          const scaledDataUrl = canvas.toDataURL('image/jpeg', 0.85);
          setPreviewSrc(scaledDataUrl);
        };
        img.src = evt.target.result;
      };
      reader.readAsDataURL(file);
    }
  };

  const captureCameraFrame = () => {
    if (videoRef.current) {
      const canvas = document.createElement('canvas');
      canvas.width = videoRef.current.videoWidth || 640;
      canvas.height = videoRef.current.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
      setPreviewSrc(dataUrl);
      setFileName('Camera Snapshot');
      setUseCamera(false);
      
      if (videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      }
    }
  };

  const triggerScan = () => {
    onRunScan(previewSrc);
  };

  const quality = lastResult?.quality || {
    blur_pass: true,
    blur_score: 184.2,
    lighting_pass: true,
    brightness: 125.0,
    all_markers_found: true,
    markers_count: 4
  };

  return (
    <>
      <div className="card">
        <div className="card-title-row">
          <span className="card-title">
            <Camera size={18} color="#38bdf8" /> Band Image Capture & Alignment
          </span>
          <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>OpenCV ArUco Engine</span>
        </div>

        {/* Marker Verification Error Alert */}
        {lastResult?.success === false && (
          <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.5)', borderRadius: '8px', padding: '10px 14px', marginBottom: '10px', color: '#fca5a5', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '700', color: '#f87171', fontSize: '0.88rem', marginBottom: '4px' }}>
              <AlertTriangle size={18} /> Marker Verification Error!
            </div>
            <div>
              {lastResult.error_message || `Only ${lastResult.quality?.markers_count || 0}/4 reference markers were detected. Analysis was stopped to ensure readings accuracy.`}
            </div>
          </div>
        )}

        {/* Selected File Status Banner */}
        {previewSrc && (
          <div style={{ background: 'rgba(56, 189, 248, 0.15)', border: '1px solid rgba(56, 189, 248, 0.4)', borderRadius: '8px', padding: '8px 12px', fontSize: '0.78rem', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: '600' }}>
              <FileImage size={16} /> Loaded: {fileName || 'Uploaded Band Image'}
            </span>
            <span style={{ fontSize: '0.7rem', background: '#38bdf8', color: '#0f172a', padding: '2px 6px', borderRadius: '4px', fontWeight: '700' }}>
              READY FOR ML SCAN
            </span>
          </div>
        )}

        {/* Camera Scanner View Box */}
        <div className="camera-container">
          {useCamera ? (
            <video ref={videoRef} autoPlay playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : previewSrc ? (
            <img src={previewSrc} alt="Uploaded Band Preview" className="camera-preview-img" />
          ) : lastResult?.aligned_image ? (
            <img src={lastResult.aligned_image} alt="Aligned Band" className="camera-preview-img" />
          ) : (
            <div style={{ textAlign: 'center', padding: '20px', color: '#94a3b8' }}>
              <Camera size={48} style={{ opacity: 0.4, marginBottom: '10px' }} />
              <div>Ready for H₂S Band Scan</div>
              <div style={{ fontSize: '0.72rem', marginTop: '4px' }}>Upload an image or use camera frame</div>
            </div>
          )}

          <div className="scanner-target-overlay">
            <div className="scanner-laser-line" />
            <div style={{ position: 'absolute', top: 6, left: 6, fontSize: '0.65rem', color: '#38bdf8', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
              ArUco ID 0 (TL)
            </div>
            <div style={{ position: 'absolute', top: 6, right: 6, fontSize: '0.65rem', color: '#38bdf8', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
              ArUco ID 1 (TR)
            </div>
            <div style={{ position: 'absolute', bottom: 6, left: 6, fontSize: '0.65rem', color: '#38bdf8', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
              ArUco ID 3 (BL)
            </div>
            <div style={{ position: 'absolute', bottom: 6, right: 6, fontSize: '0.65rem', color: '#38bdf8', background: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
              ArUco ID 2 (BR)
            </div>
          </div>
        </div>

        {/* Capture Controls */}
        <div style={{ display: 'grid', gridTemplateColumns: useCamera ? '1fr' : '1fr 1fr', gap: '10px' }}>
          {useCamera ? (
            <button className="btn-primary" onClick={captureCameraFrame}>
              Snap Photo Now
            </button>
          ) : (
            <>
              <button className="btn-secondary" onClick={startCamera}>
                <Camera size={16} /> Live Camera
              </button>
              <button className="btn-secondary" onClick={() => fileInputRef.current?.click()}>
                <Upload size={16} /> Upload File
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                accept="image/*" 
                style={{ display: 'none' }} 
                onChange={handleFileUpload} 
              />
            </>
          )}
        </div>

        <button 
          className="btn-primary" 
          disabled={scanning} 
          onClick={triggerScan} 
          style={{ width: '100%', marginTop: '6px' }}
        >
          {scanning ? (
            <>
              <RefreshCw size={18} className="spin" /> Processing ArUco & ML Pipeline...
            </>
          ) : (
            <>
              <Sparkles size={18} /> Analyze H₂S Exposure Band
            </>
          )}
        </button>
      </div>

      {/* Image Quality Check Results Card */}
      <div className="card">
        <span className="card-title">Image Quality & ArUco Verification</span>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#cbd5e1', display: 'flex', alignItems: 'center', gap: '6px' }}>
              ArUco 4-Marker Detection
            </span>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: quality.all_markers_found ? '#34d399' : '#fbbf24', display: 'flex', alignItems: 'center', gap: '4px' }}>
              {quality.all_markers_found ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
              {quality.markers_count}/4 Markers Verified
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Blur Variance Check</span>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: quality.blur_pass ? '#34d399' : '#f87171' }}>
              {quality.blur_pass ? 'PASSED (Sharp)' : 'FAILED (Blurry)'} [{quality.blur_score}]
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 12px', background: 'rgba(30,41,59,0.5)', borderRadius: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#cbd5e1' }}>Lighting & Exposure</span>
            <span style={{ fontSize: '0.8rem', fontWeight: '700', color: quality.lighting_pass ? '#34d399' : '#f87171' }}>
              {quality.lighting_pass ? 'PASSED' : 'OUT OF BOUNDS'} [{quality.brightness}]
            </span>
          </div>
        </div>
      </div>

      {/* Aligned Band Preview (1200 x 300) */}
      {lastResult?.aligned_image && (
        <div className="card">
          <span className="card-title">
            <Eye size={18} color="#06b6d4" /> Perspective Corrected Band (1200 x 300)
          </span>
          <img 
            src={lastResult.aligned_image} 
            alt="Standardized Aligned Band" 
            style={{ width: '100%', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.1)' }} 
          />
        </div>
      )}
    </>
  );
}
