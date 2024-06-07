import React, { useEffect, useRef } from "react";
import Chat from "./Chat";
import images from "../assest/images";
import style from "./chat.module.css";

const ChatSection = ({ chat, loading }) => {
  return (
    <div id="chat_section" style={{ padding: "0 10vh" }}>
      {chat.map((mess) => (
        <Chat chat={mess} />
      ))}
      {loading && (
        <div className={style.a_message}>
          <div style={{ width: 36 }}>
            <img style={{ width: 36 }} src={images.logo} alt="profile_img" />
          </div>
          loading...
        </div>
      )}
    </div>
  );
};

export default ChatSection;
