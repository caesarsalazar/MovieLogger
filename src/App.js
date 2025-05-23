import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './App.css';


export default function App() {
  const [movies, setMovies] = useState([]);
  const [form, setForm] = useState({ movie_name: '', watch_date: '', rating: '', review: '' });
  const [editingId, setEditingId] = useState(null);

  const fetchMovies = async () => {
    try {
      const res = await axios.get('http://localhost:5000/api/movies');
      setMovies(res.data);
    } catch (err) {
      alert('Failed to fetch movies');
    }
  };

  useEffect(() => {
    fetchMovies();
  }, []);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate that watch_date is not in the future
    const selectedDate = new Date(form.watch_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (selectedDate > today) {
      alert('Watch date cannot be in the future');
      return;
    }

    const url = `http://localhost:5000/api/movies${editingId ? `/${editingId}` : ''}`;
    const method = editingId ? 'put' : 'post';
    try {
      await axios[method](url, form);
      setForm({ movie_name: '', watch_date: '', rating: '', review: '' });
      setEditingId(null);
      fetchMovies();
    } catch (err) {
      alert('Failed to save movie');
    }
  };

  const handleEdit = (movie) => {
    setForm(movie);
    setEditingId(movie.movie_id);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this movie?')) return;
    try {
      await axios.delete(`http://localhost:5000/api/movies/${id}`);
      fetchMovies();
    } catch (err) {
      alert('Failed to delete movie');
    }
  };

  return (
    <div className="container">
      <h1 className="text-2xl font-bold mb-4">Movie Log</h1>

      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <input
          name="movie_name"
          value={form.movie_name}
          onChange={handleChange}
          placeholder="Movie Name"
          required
          className="border p-2 rounded"
        />
        <input
          name="watch_date"
          type="date"
          value={form.watch_date}
          onChange={handleChange}
          required
          className="border p-2 rounded"
        />
        <input
          name="rating"
          type="number"
          value={form.rating}
          onChange={handleChange}
          placeholder="Rating (0-10)"
          min="0"
          max="10"
          required
          className="border p-2 rounded"
        />
        <input
          name="review"
          value={form.review}
          onChange={handleChange}
          placeholder="Review"
          className="border p-2 rounded col-span-full"
        />
        <button type="submit" className="bg-blue-500 text-white rounded p-2">
          {editingId ? 'Update' : 'Add'} Movie
        </button>
      </form>

      <table className="table-auto w-full border-collapse border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="border border-gray-300 px-4 py-2">Name</th>
            <th className="border border-gray-300 px-4 py-2">Date</th>
            <th className="border border-gray-300 px-4 py-2">Rating</th>
            <th className="border border-gray-300 px-4 py-2">Review</th>
            <th className="border border-gray-300 px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {movies.map((movie) => (
            <tr key={movie.movie_id}>
              <td className="border border-gray-300 px-4 py-2">{movie.movie_name}</td>
              <td className="border border-gray-300 px-4 py-2">{movie.watch_date}</td>
              <td className="border border-gray-300 px-4 py-2">{movie.rating}</td>
              <td className="border border-gray-300 px-4 py-2">{movie.review}</td>
              <td className="border border-gray-300 px-4 py-2 space-x-2">
                <button onClick={() => handleEdit(movie)} className="text-blue-500">Edit</button>
                <button onClick={() => handleDelete(movie.movie_id)} className="text-red-500">Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
