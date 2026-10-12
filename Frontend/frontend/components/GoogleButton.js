"use client";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

export default function GoogleButton({ text = "continue_with", onError }) {
  const router = useRouter();
  const boxRef = useRef(null);
  const [width, setWidth] = useState(0);

  // Make the Google button as wide as the form (Google allows max 400px)
  useEffect(() => {
    if (boxRef.current) setWidth(Math.min(400, boxRef.current.offsetWidth));
  }, []);

  async function handleSuccess(response) {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/auth/google`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_token: response.credential }),
        },
      );
      const data = await res.json();

      if (!res.ok) {
        onError?.(
          typeof data.detail === "string"
            ? data.detail
            : data.detail?.[0]?.msg || "Google sign-in failed",
        );
        return;
      }

      // Temporary storage until we move to secure cookies in the login step
      localStorage.setItem("access_token", data.access_token);
      window.dispatchEvent(new Event("auth-change")); // tells the navbar to reload the user
      router.replace("/"); // replace, so back does not return to the login page
    } catch (err) {
      onError?.("Cannot reach the server");
    }
  }

  return (
    <div ref={boxRef} className="flex w-full justify-center">
      {width > 0 && (
        <GoogleOAuthProvider
          clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID}
        >
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => onError?.("Google sign-in was cancelled or failed")}
            text={text}
            theme="filled_black"
            shape="rectangular"
            size="large"
            width={width}
          />
        </GoogleOAuthProvider>
      )}
    </div>
  );
}
