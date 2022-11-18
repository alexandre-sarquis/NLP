package lematizador;

import java.util.*;
import br.usp.nilc.unitex.*;

/**
 *
 * @author Erick
 */
public class lemmar
{
    public ArrayList lemma(String entrada, String file1, String file2)
    {
    ArrayList<String> retorno = new ArrayList<String>();
    Lexicon unitexPB = new Lexicon();//inicializa objeto de acesso ao lexico
	unitexPB.CarregaDicionario(file1, file2); //carrega os arquivos .inf e .bin
	String flexoes = unitexPB.DescompactaEntradaSimples(entrada);
    DelaEntry resultado = new DelaEntry(flexoes);
    for (int i=0; i< resultado.size(); i++)//exibe cada uma das entradas encontradas no lexico, dado o token buscado
    {
        retorno.add(resultado.getEntry(i));
    }

    unitexPB.LiberaDicionario();
    return retorno; //retorna array com as entradas encontradas
    }
}
