import { Routes, Route } from 'react-router-dom'

import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ArticlePage from './pages/ArticlePage'
import DatasetPage from './pages/DatasetPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/articles/:articleId" element={<ArticlePage />} />
        <Route path="/dataset/:articleId" element={<DatasetPage />} />
      </Routes>
    </Layout>
  )
}

export default App 