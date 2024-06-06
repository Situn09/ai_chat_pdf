import "./App.css";
import Header from "./components/Header";
import Footer from "./components/Footer";
import ChatSection from "./components/ChatSection";
import { useRef, useState } from "react";

function App() {
  const [enableSendButton, setEnableSendButton] = useState(false);
  const [chat, setChat] = useState([{}]);
  const [loading, setLoading] = useState(false);

  return (
    <>
      <div className="header">
        <Header setEnableSendButton={setEnableSendButton} />
      </div>
      <ChatSection chat={chat} loading={loading} />
      <div className="footer">
        <Footer
          setChat={setChat}
          loading={loading}
          setLoading={setLoading}
          enableSendButton={enableSendButton}
          setEnableSendButton={setEnableSendButton}
        />
      </div>
    </>
  );
}

export default App;
