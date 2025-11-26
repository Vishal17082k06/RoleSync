import React, { useRef, useState, useCallback, useContext } from "react";
import "../components-css/Fileupload.css";
import { ResumeContext } from "../components/ResumeProvider"; // <-- use context

export default function FileUpload({
  multiple = true,
  accept = ".pdf,.doc,.docx,image/*",
  maxSizeBytes = 1073741824,
  onUpload = null,
}) {
  const { uploadResume } = useContext(ResumeContext); // <-- get upload function
  const inputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [dragOver, setDragOver] = useState(false);
  const [info, setInfo] = useState("");

  const id = (f) => `${f.name}_${f.size}_${f.lastModified}`;

  const addFiles = useCallback(
    (fileList) => {
      const arr = Array.from(fileList);
      const next = [...files];

      arr.forEach((f) => {
        const fid = id(f);
        if (!next.some((x) => x.id === fid)) {
          let error = null;
          if (maxSizeBytes && f.size > maxSizeBytes) {
            error = "File exceeds max size";
          }
          next.push({ file: f, id: fid, error, progress: 0 });
        }
      });

      setFiles(next);
    },
    [files, maxSizeBytes]
  );

  const handleInputChange = (e) => {
    addFiles(e.target.files);
    e.target.value = "";
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    addFiles(e.dataTransfer.files);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  };

  const removeFile = (idToRemove) => {
    setFiles((prev) => prev.filter((f) => f.id !== idToRemove));
  };

  const clearAll = () => setFiles([]);

  const friendlySize = (n) => {
    if (n < 1024) return `${n} B`;
    if (n < 1024 * 1024) return `${Math.round(n / 1024)} KB`;
    if (n < 1024 * 1024 * 1024) return `${Math.round(n / (1024 * 1024))} MB`;
    return `${Math.round(n / (1024 * 1024 * 1024))} GB`;
  };

  // This is the main upload handler now
  const uploadAll = async () => {
    if (files.length === 0) {
      setInfo("No files to upload.");
      return;
    }

    // For demo, just upload the first file to context
    const file = files[0];
    uploadResume(file);
    setInfo("Resume uploaded successfully!");

    // Clear local files if you want
    // setFiles([]);
  };

  return (
    <div className="fd-wrapper">
      <h2 className="fd-title">Resume Shortlister</h2>
      <p className="fd-sub">File upload</p>

      <div
        className={`fd-dropzone ${dragOver ? "drag-over" : ""}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        role="button"
        onClick={() => inputRef.current && inputRef.current.click()}
      >
        <input
          ref={inputRef}
          className="fd-input"
          type="file"
          accept={accept}
          multiple={multiple}
          onChange={handleInputChange}
        />

        <div className="fd-inner">
          <button
            type="button"
            className="fd-choose"
            onClick={(e) => {
              e.stopPropagation();
              inputRef.current && inputRef.current.click();
            }}
          >
            <span className="fd-choose-icon">📁</span>
            <span className="fd-choose-text">Choose Files</span>
            <span className="fd-choose-arrow">▾</span>
          </button>

          <div className="fd-note">
            Max file size {friendlySize(maxSizeBytes)}.
          </div>

          <div className="fd-draghint">or drag & drop files here</div>
        </div>
      </div>

      {/* Files list */}
      <div className="fd-files">
        {files.length === 0 ? (
          <div className="fd-empty">No files selected</div>
        ) : (
          files.map((f) => (
            <div className="fd-file" key={f.id}>
              <div className="fd-file-left">
                <div className="fd-file-name">{f.file.name}</div>
                <div className="fd-file-meta">{friendlySize(f.file.size)}</div>
                {f.error && <div className="fd-file-error">{f.error}</div>}
              </div>

              <div className="fd-file-right">
                <button
                  className="fd-remove"
                  onClick={() => removeFile(f.id)}
                  title="Remove file"
                >
                  ✕
                </button>

                <div className="fd-progress-outer" aria-hidden>
                  <div
                    className="fd-progress"
                    style={{ width: `${f.progress}%` }}
                  />
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Actions */}
      <div className="fd-actions">
        <button className="fd-clear" onClick={clearAll} disabled={files.length === 0}>
          Clear
        </button>
        <button className="fd-upload" onClick={uploadAll} disabled={files.length === 0}>
          Upload
        </button>
      </div>

      <div className="fd-info">{info}</div>
    </div>
  );
}
