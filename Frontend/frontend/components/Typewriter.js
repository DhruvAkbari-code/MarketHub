"use client";
import { useEffect, useState } from "react";

export default function Typewriter({ words }) {
  const [index, setIndex] = useState(0);
  const [text, setText] = useState("");
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    const word = words[index];
    let delay = deleting ? 50 : 100;
    if (!deleting && text === word) delay = 1200;

    const timer = setTimeout(() => {
      if (!deleting && text === word) {
        setDeleting(true);
      } else if (deleting && text === "") {
        setDeleting(false);
        setIndex((index + 1) % words.length);
      } else {
        setText(word.slice(0, text.length + (deleting ? -1 : 1)));
      }
    }, delay);

    return () => clearTimeout(timer);
  }, [text, deleting, index, words]);

  return (
    <span className="font-code text-cyan-400">
      {text}
      <span className="anim-blink">|</span>
    </span>
  );
}
