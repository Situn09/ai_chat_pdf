import React, { useEffect, useState } from "react";
import images from "../assest/images";
import style from "./header.module.css";

const Header = ({ setEnableSendButton }) => {
  const [fileName, setFileName] = useState(null);
  const uploadFile = async (file) => {
    setFileName(file.name);
    const formData = new FormData();
    formData.append("file", file);
    const url = "http://127.0.0.1:8000/uploadfile";
    await fetch(url, {
      method: "POST",
      body: formData,
    })
      .then((resp) => resp.json())
      .then((data) => {
        console.log("response data: ", data);
      })
      .catch((err) => {
        setFileName(null);
        console.log("Error : ", err);
        alert("fail to upload the file");
      });
  };
  if (fileName) setEnableSendButton(true);
  return (
    <div className={style.header}>
      <div className={style.logo_container}>
        <div className={style.logo}>
          <img src={images.logo} alt="logo" />
        </div>
        <div>
          <div style={{ fontSize: 28, fontWeight: "bolder" }}>planet</div>
          <div
            style={{ fontSize: 14, width: "fit-content", marginLeft: "auto" }}
          >
            formly <span style={{ color: "#0FA958" }}>DPhi</span>
          </div>
        </div>
      </div>
      {fileName ? (
        // if file exist then this section show
        <div
          style={{
            display: "flex",
            gap: 5,
            alignItems: "center",
          }}
        >
          <div style={{ width: 25, marginBottom: "-3px" }}>
            <img src={images.pdfIcon} alt="pdf_icon" />
          </div>
          <span className={style.file_name}>{fileName}</span>
          <label
            htmlFor="upload"
            className={`${style.add_icon} ${style.border}`}
          >
            <img src={images.addIcon} alt="add_icon" />
          </label>
          <input
            id="upload"
            style={{ display: "none" }}
            type="file"
            accept="application/pdf"
            onChange={(e) => uploadFile(e.target.files[0])}
          />
        </div>
      ) : (
        // if file doesn't exist then this section show
        <label htmlFor="upload" className={style.upload_button}>
          <div className={style.add_icon}>
            <img src={images.addIcon} alt="add_icon" />
          </div>
          <span
            style={{
              fontSize: 14,
              fontWeight: "600",
              fontFamily: "inter",
              marginLeft: 10,
            }}
          >
            Upload Pdf
          </span>
          <input
            id="upload"
            style={{ display: "none" }}
            type="file"
            accept="application/pdf"
            onChange={(e) => uploadFile(e.target.files[0])}
          />
        </label>
      )}
    </div>
  );
};
export default Header;
