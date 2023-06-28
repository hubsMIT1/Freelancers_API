import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
// import dotenv from 'react-dotenv';

// dotenv.config();
const FreelancerList = () => {
  const [freelancers, setFreelancers] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageLimit, setPageLimit] = useState(10);
  const [db, setDb] = useState('mongoDB');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchFreelancers(currentPage, db);
    
  }, [currentPage, db, pageLimit]);

  useEffect(() => {
    if (searchQuery.trim() !== '' && searchQuery !== null) {
      handleSearch();
    } else {
      fetchFreelancers(currentPage, db);
    }
  }, [searchQuery]);

  

  const fetchFreelancers = async (page, db) => {
    try {
      setLoading(true); // Set loading state
      let apiUrl = db !== 'dynamoDB' ? `${process.env.REACT_APP_MONGO_URL}/freelancers?page=${page}&limit=${pageLimit}` : `${process.env.REACT_APP_DYNAMO_URL}/freelancers?page=${page}&limit=${pageLimit}`;

     

      const response = await axios.get(apiUrl, {
        headers: { 'Access-Control-Allow-Origin': 'http://localhost:3000' },
      });
      const { data, total_pages } = response.data;

      setFreelancers(data);
      setTotalPages(total_pages);
      setLoading(false); // Clear loading state
    } catch (error) {
      
      setFreelancers([])
      setLoading(false); // Clear loading state in case of error
    }
  };

  const handleSearch = async () => {
    if (searchQuery.trim() !== '') {
      try {
        setLoading(true); // Set loading state
        const response = db === 'mongoDB' ? await axios.get(`${process.env.REACT_APP_MONGO_URL}/freelancers/search/${searchQuery}`, {
          headers: { 'Access-Control-Allow-Origin': 'http://localhost:3000' },
        }) : await axios.get(`${process.env.REACT_APP_DYNAMO_URL}/freelancers/search/${searchQuery}`);

        const { results } = response.data;
        setFreelancers('');
        setFreelancers(results);
        setTotalPages(1);
        setLoading(false); // Clear loading state
      } catch (error) {
        console.log('Error searching freelancers:', error);
        setLoading(false); // Clear loading state in case of error
      }
    }
  };

  const handlePaginationClick = (page) => {
    setCurrentPage(page);
  };

  const handleLimitChange = (e) => {
    // setPageLimit(e);
    setPageLimit(pageLimit.replace(/\D/g,''))
    
    setCurrentPage(1);
  };

  const renderTableRows = () => {
    if (freelancers && freelancers.length > 0) {
      return freelancers.map((freelancer, ind) => (
        <tr key={freelancer._id ? freelancer._id : freelancer.id}>
          <td>{ind + 1}</td>
          <td>{freelancer.first_name}</td>
          <td>{freelancer.last_name}</td>
          <td>{freelancer.email}</td>
          <td>{freelancer.phone_number}</td>
          <td>{freelancer.followers}</td>
        </tr>
      ));
    } else {
      return (
        <tr style={{ textAlign: 'center' }}>
          <td colSpan="6">Data doesn't exist!!!!</td>
        </tr>
      );
    }
  };

  const renderPagination = () => {
    const pageButtons = [];
    const visiblePageCount = 5;
    const halfVisiblePageCount = Math.floor(visiblePageCount / 2);

    let startPage = Math.max(currentPage - halfVisiblePageCount, 1);
    let endPage = startPage + visiblePageCount - 1;
    if (endPage > totalPages) {
      endPage = totalPages;
      startPage = Math.max(endPage - visiblePageCount + 1, 1);
    }

    pageButtons.push(
      <button
        key="left"
        onClick={() => handlePaginationClick(currentPage - 1)}
        disabled={startPage <= 1}
        style={{ backgroundColor: startPage <= 1 ? '#ccc' : '#4caf50' }}
      >
        &#8249;
      </button>
    );

    for (let i = startPage; i <= endPage; i++) {
      pageButtons.push(
        <button
          key={i}
          onClick={() => handlePaginationClick(i)}
          className={i === currentPage ? 'active' : ''}
        >
          {i}
        </button>
      );
    }

    pageButtons.push(
      <button
        key="right"
        onClick={() => handlePaginationClick(currentPage + 1)}
        disabled={endPage >= totalPages}
        style={{ backgroundColor: endPage >= totalPages ? '#ccc' : '#4caf50' }}
      >
        &#8250;
      </button>
    );

    return <div className="pagination">{pageButtons}</div>;
  };

  return (
    <div>
      <div className="search-container">
        <div>
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search..."
          />
          <button onClick={handleSearch}>
            {loading ? (
              <span>Loading...</span>
            ) : (
              <span>search</span>
            )}
          </button>
          <input
            type="number"
            value={pageLimit}
            onChange={(e) => setPageLimit(e.target.value.replace(/\D/g, ''))}
            placeholder="Limit"
          />

          <button onClick={handleLimitChange}>
          {loading ? (
              <span>Loading...</span>
            ) : (
              <span>Page Limit</span>
            )}
          </button>
          <select
            value={db}
            onChange={(e) => {
              setDb(e.target.value);
            }}
          >
            <option value="mongoDB">mongoDB</option>
            <option value="dynamoDB">dynamoDB</option>
          </select>
        </div>
        <div>{renderPagination()}</div>
      </div>
      <table>
        <thead>
          <tr>
            <th>S.No</th>
            <th>First Name</th>
            <th>Last Name</th>
            <th>Email</th>
            <th>Phone Number</th>
            <th>Followers</th>
          </tr>
        </thead>
        <tbody>
       
          {loading ? (
            <tr className="loader-container">
      	      <td className="spinner"></td>
          </tr>
          ) : (
            <>
              {freelancers && freelancers.length > 0 ? (
                renderTableRows()
              ) : (
                <tr>
                  <td colSpan="6">Data doesn't exist!!</td>
                </tr>
              )}
            </>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default FreelancerList;
