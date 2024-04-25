import React from "react";

import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import {
  ErrorBoundary,
  Facet,
  SearchProvider,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  Sorting,
  WithSearch
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

import {
  buildSortOptionsFromConfig,
  getConfig,
  getFacetFields
} from "./config/config-helper";

const connector = new ElasticsearchAPIConnector({
  host: "http://172.31.25.132:9200",
  index: "cv-transcriptions"
});

const config = {
  alwaysSearchOnInitialLoad: true,
  apiConnector: connector,
  searchQuery: {
    search_fields: {
      generated_text: { weight: 1 },
      age: { weight: 0.5 },
      gender: { weight: 0.5 },
      accent: { weight: 0.5 }
    },
    result_fields: {
      generated_text: { raw: {} },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} }
    },
    disjunctiveFacets: ["age", "gender", "accent"],
    facets: {
      age: { type: "value" },
      gender: { type: "value" },
      accent: { type: "value" }
    }
  }
};

export default function App() {
  return (
    <SearchProvider config={config}>
      <WithSearch mapContextToProps={({ wasSearched }) => ({ wasSearched })}>
        {({ wasSearched }) => (
          <div className="App">
            <ErrorBoundary>
              <Layout
                header={
                  <SearchBox
                    autocompleteMinimumCharacters={3}
                    autocompleteResults={{
                      linkTarget: "_blank",
                      sectionTitle: "Results",
                      titleField: "generated_text",
                      urlField: "gender",
                      shouldTrackClickThrough: true
                    }}
                    autocompleteSuggestions={{
                      sectionTitle: "Suggestions",
                      suggester: "suggest",
                      field: "generated_text",
                      size: 5
                    }}
                    debounceLength={0}
                  />
                }
                sideContent={
                  <div>
                    {wasSearched && (
                      <Sorting
                        label={"Sort by"}
                        sortOptions={buildSortOptionsFromConfig()}
                      />
                    )}
                    {getFacetFields().map(field => (
                      <Facet key={field} field={field} label={field} />
                    ))}
                  </div>
                }
                bodyContent={
                  <Results
                    titleField="generated_text"
                    urlField="gender"
                    thumbnailField=""
                    shouldTrackClickThrough={true}
                  />
                }
                bodyHeader={
                  <React.Fragment>
                    {wasSearched && <PagingInfo />}
                    {wasSearched && <ResultsPerPage />}
                  </React.Fragment>
                }
                bodyFooter={<Paging />}
              />
            </ErrorBoundary>
          </div>
        )}
      </WithSearch>
    </SearchProvider>
  );
}
