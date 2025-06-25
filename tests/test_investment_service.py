"""Tests para el servicio de inversiones."""

from __future__ import annotations

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import Mock, patch

from src.services.investment_service import InvestmentService
from src.database.models import Investment, InvestmentType


class TestInvestmentService:
    """Tests para InvestmentService."""

    @pytest.fixture
    def mock_session(self):
        """Mock de sesión de base de datos."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Instancia del servicio con mock de sesión."""
        return InvestmentService(db_session=mock_session)

    def test_create_investment_success(self, service, mock_session):
        """Test crear inversión exitosamente."""
        # Act
        result = service.create_investment(
            name="AAPL",
            investment_type=InvestmentType.STOCK,
            initial_amount=Decimal("1000.00"),
            shares=Decimal("10.0"),
            purchase_price=Decimal("100.00")
        )

        # Assert
        assert isinstance(result, Investment)
        assert result.name == "AAPL"
        assert result.investment_type == InvestmentType.STOCK
        assert result.initial_amount == Decimal("1000.00")
        assert result.current_value == Decimal("1000.00")
        assert result.shares == Decimal("10.0")
        assert result.purchase_price == Decimal("100.00")
        assert result.is_active is True

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    def test_create_investment_minimal_params(self, service, mock_session):
        """Test crear inversión con parámetros mínimos."""
        # Act
        result = service.create_investment(
            name="BTC",
            investment_type=InvestmentType.CRYPTO,
            initial_amount=Decimal("500.00")
        )

        # Assert
        assert result.name == "BTC"
        assert result.investment_type == InvestmentType.CRYPTO
        assert result.initial_amount == Decimal("500.00")
        assert result.current_value == Decimal("500.00")
        assert result.shares is None
        assert result.purchase_price is None

    def test_create_investment_with_date(self, service, mock_session):
        """Test crear inversión con fecha específica."""
        # Arrange
        purchase_date = date(2025, 1, 15)

        # Act
        result = service.create_investment(
            name="TSLA",
            investment_type=InvestmentType.STOCK,
            initial_amount=Decimal("2000.00"),
            purchase_date=purchase_date
        )

        # Assert
        assert result.purchase_date == purchase_date

    def test_get_investments_active_only(self, service, mock_session):
        """Test obtener solo inversiones activas."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = service.get_investments(active_only=True)

        # Assert
        assert result == []
        mock_session.query.assert_called_once_with(Investment)
        mock_query.filter.assert_called_once()

    def test_get_investments_all(self, service, mock_session):
        """Test obtener todas las inversiones."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        result = service.get_investments(active_only=False)

        # Assert
        assert result == []
        mock_session.query.assert_called_once_with(Investment)

    def test_get_investment_by_id_found(self, service, mock_session):
        """Test obtener inversión por ID existente."""
        # Arrange
        mock_investment = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_investment

        # Act
        result = service.get_investment_by_id("inv-123")

        # Assert
        assert result == mock_investment

    def test_get_investment_by_id_not_found(self, service, mock_session):
        """Test obtener inversión por ID inexistente."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = service.get_investment_by_id("inv-999")

        # Assert
        assert result is None

    def test_create_investment_database_error(self, service, mock_session):
        """Test error en base de datos al crear inversión."""
        # Arrange
        mock_session.commit.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            service.create_investment(
                name="AAPL",
                investment_type=InvestmentType.STOCK,
                initial_amount=Decimal("1000.00")
            )

        mock_session.rollback.assert_called_once()

    def test_update_investment_value_success(self, service, mock_session):
        """Test actualizar valor de inversión."""
        # Arrange
        mock_investment = Mock()
        mock_investment.current_value = Decimal("1000.00")
        service.get_investment_by_id = Mock(return_value=mock_investment)

        # Act
        result = service.update_investment_value("inv-123", Decimal("1100.00"))

        # Assert
        assert result == mock_investment
        assert mock_investment.current_value == Decimal("1100.00")
        assert isinstance(mock_investment.last_updated, datetime)
        mock_session.commit.assert_called_once()

    def test_update_investment_value_not_found(self, service, mock_session):
        """Test actualizar valor de inversión inexistente."""
        # Arrange
        service.get_investment_by_id = Mock(return_value=None)

        # Act
        result = service.update_investment_value("inv-999", Decimal("1100.00"))

        # Assert
        assert result is None
        mock_session.commit.assert_not_called()
