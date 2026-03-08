import { PublicClientApplication } from "@azure/msal-browser";

const msalConfig = {
    auth: {
        clientId: "a87eb6fc-df49-4d07-8a92-0b3a969f88b2",
        authority: "https://login.microsoftonline.com/823cde44-4433-456d-b801-bdf0ab3d41fc",
        redirectUri: window.location.origin + "/auth/callback",
    },
    cache: {
        cacheLocation: "localStorage",
        storeAuthStateInCookie: false,
    }
};

export const msalInstance = new PublicClientApplication(msalConfig);

let isMsalInitialized = false;
export const getMsalInstance = async () => {
    if (!isMsalInitialized) {
        await msalInstance.initialize();
        isMsalInitialized = true;
    }
    return msalInstance;
};
