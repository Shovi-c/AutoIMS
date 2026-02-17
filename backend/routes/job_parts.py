"""
Job Parts Used API routes.
"""
from flask import Blueprint, request, jsonify
from controllers import job_parts as jp_ctrl
from utils.jwt_utils import token_required

job_parts_bp = Blueprint('job_parts', __name__, url_prefix='/api/job-parts')


@job_parts_bp.route('/job/<int:job_id>', methods=['GET'])
@token_required
def get_parts_for_job(current_user, job_id):
    """Get all parts used in a specific job."""
    try:
        # Validate job exists
        if not jp_ctrl.job_exists(job_id):
            return jsonify({'error': 'Job not found'}), 404
        
        parts = jp_ctrl.get_parts_for_job(job_id)
        total_cost = jp_ctrl.get_total_parts_cost(job_id)
        
        return jsonify({
            'message': 'Parts retrieved successfully',
            'job_id': job_id,
            'parts': parts,
            'total_cost': total_cost
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get parts: {str(e)}'}), 500


@job_parts_bp.route('', methods=['POST'])
@token_required
def add_part_to_job(current_user):
    """
    Add a part to a job. Updates inventory automatically.
    
    Expected JSON:
    {
        "job_id": 1,
        "part_id": 5,
        "quantity_used": 2
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        job_id = data.get('job_id')
        part_id = data.get('part_id')
        quantity_used = data.get('quantity_used')
        
        # Validate required fields
        if not job_id:
            return jsonify({'error': 'job_id is required'}), 400
        
        if not part_id:
            return jsonify({'error': 'part_id is required'}), 400
        
        if not quantity_used:
            return jsonify({'error': 'quantity_used is required'}), 400
        
        try:
            quantity_used = int(quantity_used)
        except ValueError:
            return jsonify({'error': 'quantity_used must be an integer'}), 400
        
        if quantity_used <= 0:
            return jsonify({'error': 'quantity_used must be positive'}), 400
        
        # Validate job exists
        if not jp_ctrl.job_exists(job_id):
            return jsonify({'error': 'Job not found'}), 404
        
        # Validate part exists
        if not jp_ctrl.part_exists(part_id):
            return jsonify({'error': 'Part not found'}), 404
        
        # Add part to job (also updates inventory)
        result, error = jp_ctrl.add_part_to_job(job_id, part_id, quantity_used)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Part added to job successfully',
            'job_part': result
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to add part: {str(e)}'}), 500


@job_parts_bp.route('/<int:job_part_id>', methods=['DELETE'])
@token_required
def remove_part_from_job(current_user, job_part_id):
    """Remove a part from a job and restore inventory."""
    try:
        success, error = jp_ctrl.remove_part_from_job(job_part_id)
        
        if not success:
            return jsonify({'error': error or 'Failed to remove part'}), 404
        
        return jsonify({
            'message': 'Part removed from job successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to remove part: {str(e)}'}), 500


@job_parts_bp.route('/job/<int:job_id>/total', methods=['GET'])
@token_required
def get_parts_total(current_user, job_id):
    """Get total cost of parts used in a job."""
    try:
        if not jp_ctrl.job_exists(job_id):
            return jsonify({'error': 'Job not found'}), 404
        
        total = jp_ctrl.get_total_parts_cost(job_id)
        
        return jsonify({
            'message': 'Total calculated successfully',
            'job_id': job_id,
            'total_parts_cost': total
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to calculate total: {str(e)}'}), 500
