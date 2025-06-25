"""Tests para el servicio de presupuestos."""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

from src.services.budget_service import BudgetService
from src.database.models import Budget, BudgetCategory, Category


class TestBudgetService:
    """Tests para BudgetService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sesión de base de datos."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Instancia del servicio con mock de sesión."""
        return BudgetService(db_session=mock_session)

    def test_create_budget_success(self, service, mock_session):
        """Test crear presupuesto exitosamente."""
        # Act
        result = service.create_budget(
            name="Test Budget",
            period_type="monthly",
            year=2025,
            month=1
        )

        # Assert
        assert isinstance(result, Budget)
        assert result.name == "Test Budget"
        assert result.period_type == "monthly"
        assert result.year == 2025
        assert result.month == 1
        assert result.is_active is True

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_budget_yearly(self, service, mock_session):
        """Test crear presupuesto anual."""
        # Act
        result = service.create_budget(
            name="Yearly Budget",
            period_type="yearly",
            year=2025,
            description="Annual planning"
        )

        # Assert
        assert result.period_type == "yearly"
        assert result.month is None
        assert result.description == "Annual planning"

    def test_add_budget_category_success(self, service, mock_session):
        """Test agregar categoría a presupuesto."""
        # Arrange
        mock_category = Mock()
        mock_category.id = "cat-123"
        service._get_or_create_category = Mock(return_value=mock_category)

        # Act
        result = service.add_budget_category(
            budget_id="budget-456",
            category_name="food",
            allocated_amount=Decimal("500.00"),
            description="Food expenses"
        )

        # Assert
        assert isinstance(result, BudgetCategory)
        assert result.budget_id == "budget-456"
        assert result.category_id == "cat-123"
        assert result.allocated_amount == Decimal("500.00")
        assert result.description == "Food expenses"
          mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_get_budgets_active_only(self, service, mock_session):
        """Test obtener solo presupuestos activos."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = service.get_budgets(active_only=True)

        # Assert
        assert result == []
        mock_session.query.assert_called_once_with(Budget)
        mock_query.filter.assert_called_once()

    def test_get_budgets_all(self, service, mock_session):
        """Test obtener todos los presupuestos."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = service.get_budgets(active_only=False)

        # Assert
        assert result == []
        mock_session.query.assert_called_once_with(Budget)

    def test_create_budget_database_error(self, service, mock_session):
        """Test error en base de datos al crear presupuesto."""
        # Arrange
        mock_session.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            service.create_budget(
                name="Test Budget",
                period_type="monthly",
                year=2025
            )

        mock_session.rollback.assert_called_once()

    def test_add_budget_category_database_error(self, service, mock_session):
        """Test error en base de datos al agregar categoría."""
        # Arrange
        service._get_or_create_category = Mock(return_value=Mock(id="cat-123"))
        mock_session.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            service.add_budget_category(
                budget_id="budget-456",
                category_name="food",
                allocated_amount=Decimal("500.00")
            )

        mock_session.rollback.assert_called_once()

    def test_get_or_create_category_integration(self, service, mock_session):
        """Test integración con _get_or_create_category."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = service._get_or_create_category("test_category")

        # Assert
        assert isinstance(result, Category)
        assert result.name == "test_category"
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()
