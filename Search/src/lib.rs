use strsim::levenshtein;
use pyo3::{prelude::*, types::PyList};
use rayon::prelude::*;

/// Formats the sum of two numbers as string.
#[pyfunction]
fn parallel_search(array: &PyList, looking_for: &str) -> PyResult<String> {
    let array: Vec<String> = array.extract()?;

    if let Ok(best) = array.par_iter().min_by_key(|el| levenshtein(el, looking_for)).ok_or("fail") {
        return Ok(best.to_string())
    }
    
    Ok("fail".to_string())
}

/// A Python module implemented in Rust.
#[pymodule]
fn Search(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parallel_search, m)?)?;
    Ok(())
}
