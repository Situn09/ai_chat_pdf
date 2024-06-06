import React from "react";
import images from "../assest/images";
import style from "./chat.module.css";

const Chat = ({ chat, enableSendButton }) => {
  const { question, answer } = chat;
  if (!question && !answer) return;
  return (
    <div>
      <div>
        {question && (
          <div className={style.q_message}>
            {question}
            <div style={{ width: 36 }}>
              <img src={images.user} alt="profile_img" />
            </div>
          </div>
        )}
      </div>
      <div>
        {answer && (
          <div className={style.a_message}>
            <div style={{ width: 36 }}>
              <img src={images.logo} alt="profile_img" />
            </div>
            {answer}
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
