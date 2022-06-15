import Head from 'next/head'
import { useState, useMemo } from 'react';
import { search } from "backend/search";

export default function Home() {
  const [isFocused, setIsFocused] = useState(false);
  const headerClassName = isFocused
    ? "header wide"
    : "header";

  const eventHandlers = useMemo(() => ({
    onFocus: () => setIsFocused(true),
    onBlur: () => setIsFocused(false),
  }), []);

  const keyPressHandler = (e) => {
    if (e.key === "Enter") {
      if (e.target.value === "") {
        setAppStyle("glass");
        setResults([])
      } else {
        setAppStyle("dark");
        search(e.target.value)
          .then(response => setResults(response.data))
          .catch(error => { alert("Service unavailable. Please try again later.") }
          );
      }
    }
  }

  const [results, setResults] = useState({});

  const [appStyle, setAppStyle] = useState("");

  return (
    <div className="container">
      <Head>
        <title>Spidey Search</title>
        <link rel="icon" href="/favicon.ico" />
        <link rel="stylesheet" href="/style.css" />
      </Head>

      <main>
        <div id="app" className={appStyle}>
          <div className={headerClassName}>
            <div className="titleContainer">
              <h1 onClick={()=>setAppStyle("glass")} className="title"><span>S</span><span>p</span><span>i</span><span>d</span><span>e</span><span>y</span> Search</h1>
            </div>
            <div className="searchBarContainer">
              <input className='searchBar' placeholder="Search" {...eventHandlers} onKeyPress={keyPressHandler} />
            </div>
          </div>
          {!!results.results &&
            <div className="results">
              <p>search time: {results.time.toFixed(5)} milliseconds</p>
              {
                results.results.map((result, index) =>
                  <div key={index} className="search-result">
                    <div>
                      <a href={result[1]}>{result[0]}</a>
                    </div>
                    <div>
                      <a href={result[1]}>{result[1]}</a>
                    </div>
                  </div>
                )
              }
            </div>
          }
        </div>
      </main>
    </div>
  )
}
