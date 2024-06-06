import React, { useState } from "react";
import images from "../assest/images";
import style from "./footer.module.css";

const Footer = ({
  setChat,
  enableSendButton,
  setEnableSendButton,
  setLoading,
  loading,
}) => {
  const [question, setQuestion] = useState("");

  const sendQuery = async (question) => {
    if (loading) {
      alert("wait for response");
      return;
    }
    if (!enableSendButton) {
      alert("first upload file");
      return;
    }
    if (question === "" || !question) {
      alert("write something");
      return;
    }
    setChat((chat) => [...chat, { question }]);
    setLoading(true);
    setEnableSendButton(false);
    const url = "http://127.0.0.1:8000/ask-question";
    await fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question }),
    })
      .then((resp) => resp.json())
      .then((data) => {
        setLoading(false);
        setEnableSendButton(true);
        setChat((chat) => [...chat, data]);
        console.log("response data: ", data);
      })
      .catch((err) => {
        console.log("Error: ", err);
        alert("fail to fetch answer");
        setLoading(false);
      });
  };

  const onKeyDownHandler = (e) => {
    if (e.key === "Enter" && enableSendButton) {
      sendQuery(question);
    } else if (e.key === "Enter" && !enableSendButton) {
      alert("first upload file");
    }
  };

  return (
    <div className={style.input_container}>
      <input
        type="text"
        placeholder="Send a message..."
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={(e) => onKeyDownHandler(e)}
      />
      <div className={style.send} onClick={() => sendQuery(question)}>
        <img src={images.sendIcon} alt="send_icon" />
      </div>
    </div>
  );
};

export default Footer;
