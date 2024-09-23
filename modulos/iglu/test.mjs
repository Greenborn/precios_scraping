/*{"name":"IGLU Helados","description":"Helados + café",
"slug":"igluhelados","platforms":["ios","android","web"],
"version":"2.1.0","orientation":"portrait",
"icon":"./assets/images/icon.png","scheme":"igluhelados",
"userInterfaceStyle":"light",
"splash":{"image":"./assets/images/splash.png","resizeMode":"cover","backgroundColor":"#FF6600"},
"updates":{"enabled":false},"assetBundlePatterns":["/*"],
"ios":{"bundleIdentifier":"com.walnut.ecommerce.shops.iglu","buildNumber":"2",
"supportsTablet":false,"googleServicesFile":"./GoogleService-Info.plist"},
"android":{"package":"com.walnut.ecommerce.shops.iglu","versionCode":32,"googleServicesFile":"./google-services.json"},
"web":{"config":{"firebase":{"apiKey":"AIzaSyCiVBSl2KTRZD-rQiPU0jNYBtXDP2LYFr4",
"authDomain":"iglu-helados-prod.firebaseapp.com",
"databaseURL":"https://iglu-helados-prod.firebaseio.com",
"projectId":"iglu-helados-prod",
"storageBucket":"iglu-helados-prod.appspot.com",
"messagingSenderId":"927765391568",
"appId":"1:927765391568:web:9b88ad4e40ac38f12e16d5","measurementId":"G-VHQ6N6L6R6"}}},
"plugins":["sentry-expo"],"extra":{"eas":{"projectId":"fd04bef0-226a-40c6-b972-de3dd49a86ae"}},"owner":"fernandopena","sdkVersion":"48.0.0"}*/
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore/lite';


var firebaseConfig = {
    apiKey: "AIzaSyCiVBSl2KTRZD-rQiPU0jNYBtXDP2LYFr4",
    authDomain: "iglu-helados-prod.firebaseapp.com",
    // The value of `databaseURL` depends on the location of the database
    databaseURL: "https://iglu-helados-prod.firebaseio.com",
    projectId: "iglu-helados-prod",
    storageBucket: "iglu-helados-prod.appspot.com",
    messagingSenderId: "927765391568",
    appId: "1:927765391568:web:9b88ad4e40ac38f12e16d5",
    // For Firebase JavaScript SDK v7.20.0 and later, `measurementId` is an optional field
    measurementId: "G-VHQ6N6L6R6",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function getData(db) {
    const citiesCol = collection(db, "price");
    const citySnapshot = await getDocs(citiesCol);
    const cityList = citySnapshot.docs.map(doc => doc.data());
    return cityList;
}

setTimeout(async () => {
    let data = await getData(db)
    if (data)
        console.log( data )
}, 400)


