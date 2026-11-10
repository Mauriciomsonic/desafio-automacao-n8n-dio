import re
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PerfilInvestidor(str, Enum):
    CONSERVADOR = "Conservador"
    MODERADO = "Moderado"
    ARROJADO = "Arrojado"


class Cliente(BaseModel):
    nome: str = Field(..., min_length=2)
    email: Optional[str] = None
    saldo: Decimal = Field(..., ge=0)
    perfil: PerfilInvestidor

    @field_validator("perfil", mode="before")
    @classmethod
    def parse_perfil(cls, v):
        if isinstance(v, PerfilInvestidor):
            return v
        s = str(v).strip().capitalize()
        return s

    @field_validator("saldo", mode="before")
    @classmethod
    def parse_saldo(cls, v):
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        s = str(v)
        # Remove 'R$' e espaços
        s = s.replace("R$", "").strip()
        # Tratamento de formato brasileiro: 1.234,56 ou 1.234.567,89
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s:
            s = s.replace(",", ".")
        # Remove quaisquer outros caracteres não numéricos exceto dígito, ponto ou traço
        s = re.sub(r"[^\d.-]", "", s)
        try:
            return Decimal(s) if s else Decimal("0")
        except InvalidOperation:
            return Decimal("0")


class Investimento(BaseModel):
    perfil: PerfilInvestidor
    produto: str
    minimo: Decimal = Field(..., ge=0)
    rentabilidade: str

    @field_validator("perfil", mode="before")
    @classmethod
    def parse_perfil_invest(cls, v):
        if isinstance(v, PerfilInvestidor):
            return v
        return str(v).strip().capitalize()

    @field_validator("minimo", mode="before")
    @classmethod
    def parse_minimo(cls, v):
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        s = re.sub(r"[^\d.-]", "", str(v).replace(",", "."))
        try:
            return Decimal(s) if s else Decimal("0")
        except InvalidOperation:
            return Decimal("0")


class Recomendacao(BaseModel):
    cliente: Cliente
    investimentos_recomendados: List[Investimento]
    mensagem: str
