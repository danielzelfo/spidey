import Config from "backend/config.json";
import Axios from "axios";

export async function search(searchQuery) {
    const requestParams = {
        q: searchQuery
    };

    const options = {
        method: "GET",
        baseURL: Config.search.url, 
        url: "/",
        params: requestParams 
    }

    return Axios.request(options);
}