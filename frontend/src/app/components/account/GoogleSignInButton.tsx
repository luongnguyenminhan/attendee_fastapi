"use client";
import Image from "next/image";
import React from "react";

interface GoogleSignInButtonProps {
  label?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({
  label = "Sign in with Google",
  onClick,
  disabled = false,
}) => (
  <button
    type="button"
    className="gsi-material-button flex items-center justify-center w-full border border-gray-300 rounded-md bg-white dark:bg-neutral-900 dark:border-neutral-700 shadow-sm py-2 px-4 transition hover:bg-gray-50 dark:hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed"
    onClick={onClick}
    disabled={disabled}
  >
    <span className="gsi-material-button-content-wrapper flex items-center w-full justify-center">
      <Image
        src="/google.svg"
        alt="Google"
        className="gsi-material-button-icon mr-3 h-5 w-5"
        width={20}
        height={20}
      />
      <span className="gsi-material-button-contents font-medium text-sm text-gray-900 dark:text-gray-100">
        {label}
      </span>
    </span>
  </button>
);

export default GoogleSignInButton;
