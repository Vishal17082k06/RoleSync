import { createContext, useState } from "react";

export const ResumeContext = createContext();

export const ResumeProvider = ({ children }) => {
  const [resume, setResume] = useState(null);

  const uploadResume = (file) => {
    if (!file) return;
    setResume({ file, url: URL.createObjectURL(file) });
  };

  return (
    <ResumeContext.Provider value={{ resume, uploadResume }}>
      {children}
    </ResumeContext.Provider>
  );
};
